"""
메타데이터 유틸리티
통일된 메타데이터 형식을 보장합니다.
"""

from typing import Dict, Optional
from api.schemas.video import VideoMetadata


def normalize_metadata(metadata: Dict, video_id: Optional[str] = None) -> Dict:
    """
    메타데이터를 표준 형식으로 정규화합니다.
    
    Args:
        metadata: 원본 메타데이터 딕셔너리
        video_id: 비디오 ID (metadata에 없을 경우 사용)
    
    Returns:
        정규화된 메타데이터 딕셔너리
    """
    # video_id 보장
    if 'video_id' not in metadata or not metadata['video_id']:
        metadata['video_id'] = video_id or ''
    
    # 필수 필드 기본값 설정
    normalized = {
        'video_id': metadata.get('video_id', ''),
        'title': metadata.get('title', 'Unknown Title'),
        'channel': metadata.get('channel', 'Unknown Channel'),
        'upload_date': metadata.get('upload_date'),
        'duration': metadata.get('duration'),
        'view_count': metadata.get('view_count'),
        'like_count': metadata.get('like_count'),
        'description': metadata.get('description'),
        'thumbnail_url': metadata.get('thumbnail_url'),
    }
    
    return normalized


def validate_metadata(metadata: Dict) -> VideoMetadata:
    """
    메타데이터를 검증하고 VideoMetadata 객체로 변환합니다.
    
    Args:
        metadata: 메타데이터 딕셔너리
    
    Returns:
        VideoMetadata 객체
    
    Raises:
        ValidationError: 메타데이터 형식이 올바르지 않을 경우
    """
    normalized = normalize_metadata(metadata)
    return VideoMetadata(**normalized)
