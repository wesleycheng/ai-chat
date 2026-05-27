import os
import uuid
from datetime import datetime
from typing import List, Optional

import aiofiles
import filetype
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import get_current_user
from ..models.models import File as DBFile, FileStatus, User
from ..schemas.schemas import FileCreate, FileResponse, FileListResponse

router = APIRouter(prefix="/files", tags=["files"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".txt", ".md", ".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


async def validate_file(file: UploadFile) -> None:
    """验证文件类型和大小"""
    # 检查文件大小
    contents = await file.read(MAX_FILE_SIZE)
    await file.seek(0)
    
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"文件大小超过 {MAX_FILE_SIZE / 1024 / 1024}MB 限制")
    
    # 检查文件类型
    kind = filetype.guess(contents)
    if kind is None or f".{kind.extension}" not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="不支持的文件类型")
    
    return kind


async def parse_file_content(file_path: str, extension: str) -> Optional[str]:
    """解析文件内容为纯文本"""
    ext = extension.lower()
    
    try:
        if ext == ".pdf":
            return await parse_pdf(file_path)
        elif ext in [".docx", ".doc"]:
            return await parse_docx(file_path)
        elif ext in [".xlsx", ".xls"]:
            return await parse_xlsx(file_path)
        elif ext in [".txt", ".md"]:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                return await f.read()
        elif ext in [".jpg", ".jpeg", ".png"]:
            return "[图片文件]"  # 图片需要 OCR 处理
    except Exception as e:
        return f"[解析失败: {str(e)}]"
    
    return None


async def parse_pdf(file_path: str) -> str:
    """解析 PDF"""
    import pymupdf
    text_parts = []
    with pymupdf.open(file_path) as doc:
        for page in doc:
            text_parts.append(page.get_text())
    return "\n".join(text_parts)


async def parse_docx(file_path: str) -> str:
    """解析 DOCX"""
    from docx import Document
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])


async def parse_xlsx(file_path: str) -> str:
    """解析 XLSX"""
    from openpyxl import load_workbook
    wb = load_workbook(file_path, read_only=True)
    parts = []
    for sheet in wb.worksheets:
        for row in sheet.iter_rows(values_only=True):
            if any(row):
                parts.append(" | ".join([str(cell) if cell else "" for cell in row]))
    return "\n".join(parts)


@router.post("/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """上传文件"""
    # 验证文件
    try:
        kind = await validate_file(file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 生成文件路径
    file_ext = f".{kind.extension}"
    file_id = str(uuid.uuid4())
    file_path = os.path.join(
        os.getenv("UPLOAD_DIR", "./uploads"),
        f"{file_id}{file_ext}"
    )
    
    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # 保存文件
    contents = await file.read()
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(contents)
    
    # 创建数据库记录
    db_file = DBFile(
        id=file_id,
        user_id=current_user.id,
        filename=file.filename,
        file_ext=file_ext,
        file_size=len(contents),
        file_path=file_path,
        parse_status=FileStatus.PENDING,
    )
    db.add(db_file)
    await db.commit()
    await db.refresh(db_file)
    
    # TODO: 提交异步任务解析文件内容
    # await file_parse_task.delay(file_id)
    
    return db_file


@router.get("", response_model=FileListResponse)
async def list_files(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取文件列表"""
    stmt = select(DBFile).where(DBFile.user_id == current_user.id).order_by(DBFile.created_at.desc())
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    files = result.scalars().all()
    
    count_stmt = select(DBFile).where(DBFile.user_id == current_user.id)
    count_result = await db.execute(count_stmt)
    total = len(count_result.scalars().all())
    
    return {"items": files, "total": total}


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取文件详情"""
    stmt = select(DBFile).where(DBFile.id == file_id, DBFile.user_id == current_user.id)
    result = await db.execute(stmt)
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return file


@router.get("/{file_id}/status")
async def get_file_status(
    file_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取文件解析状态"""
    stmt = select(DBFile).where(DBFile.id == file_id, DBFile.user_id == current_user.id)
    result = await db.execute(stmt)
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return {
        "id": file.id,
        "filename": file.filename,
        "parse_status": file.parse_status.value,
        "parse_error": file.parse_error,
    }


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除文件"""
    stmt = select(DBFile).where(DBFile.id == file_id, DBFile.user_id == current_user.id)
    result = await db.execute(stmt)
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 删除物理文件
    if file.file_path and os.path.exists(file.file_path):
        os.remove(file.file_path)
    
    # 删除数据库记录
    await db.delete(file)
    await db.commit()
    
    return {"message": "删除成功"}