"""文件上传 API"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID, uuid4
import os
import aiofiles
import magic

from ..core import get_db, settings
from ..models import User, File
from ..schemas import FileResponse, SuccessResponse
from .auth import get_current_user

router = APIRouter(prefix="/files", tags=["文件"])


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(filename)[1].lower()


def validate_file(file: UploadFile) -> tuple[bool, str]:
    """验证文件"""
    # 检查扩展名
    ext = get_file_extension(file.filename or "")
    if ext not in settings.ALLOWED_EXTENSIONS:
        return False, f"不支持的文件类型: {ext}"
    
    return True, ""


@router.post("/upload", response_model=FileResponse, status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传文件"""
    # 验证文件
    is_valid, error_msg = validate_file(file)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # 读取文件内容检查大小
    content = await file.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制 ({settings.MAX_FILE_SIZE // 1024 // 1024}MB)"
        )
    
    # 检测真实 MIME 类型
    mime_type = magic.from_buffer(content, mime=True)
    
    # 生成存储路径
    file_id = uuid4()
    ext = get_file_extension(file.filename or "")
    storage_name = f"{file_id}{ext}"
    storage_path = os.path.join(settings.UPLOAD_DIR, storage_name)
    
    # 确保上传目录存在
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # 保存文件
    async with aiofiles.open(storage_path, "wb") as f:
        await f.write(content)
    
    # 创建数据库记录
    file_record = File(
        id=file_id,
        user_id=current_user.id,
        filename=file.filename,
        file_path=storage_path,
        file_size=len(content),
        mime_type=mime_type,
        parse_status="pending",
    )
    db.add(file_record)
    await db.commit()
    await db.refresh(file_record)
    
    # TODO: 触发异步解析任务
    
    return file_record


@router.get("", response_model=List[FileResponse])
async def list_files(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取文件列表"""
    result = await db.execute(
        select(File)
        .where(File.user_id == current_user.id)
        .order_by(File.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取文件详情"""
    result = await db.execute(
        select(File).where(
            File.id == file_id,
            File.user_id == current_user.id,
        )
    )
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    return file


@router.get("/{file_id}/status")
async def get_file_status(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取文件解析状态"""
    result = await db.execute(
        select(File).where(
            File.id == file_id,
            File.user_id == current_user.id,
        )
    )
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return {
        "file_id": file.id,
        "status": file.parse_status,
        "chunk_count": file.chunk_count,
        "error_message": file.error_message,
    }


@router.delete("/{file_id}", status_code=204)
async def delete_file(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除文件"""
    result = await db.execute(
        select(File).where(
            File.id == file_id,
            File.user_id == current_user.id,
        )
    )
    file = result.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 删除物理文件
    if os.path.exists(file.file_path):
        os.remove(file.file_path)
    
    # 删除数据库记录
    await db.delete(file)
    await db.commit()