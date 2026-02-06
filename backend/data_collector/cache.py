"""
데이터 캐싱 관리 모듈
"""
import json
import os
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger
import hashlib


class CacheManager:
    """데이터 캐싱 관리 클래스 (로컬 파일 시스템 기반)"""
    
    def __init__(self, cache_dir: str = "backend/cache"):
        """
        초기화
        
        Args:
            cache_dir: 캐시 디렉토리 경로
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = 86400  # 1일 (초 단위)
        
        logger.info(f"CacheManager 초기화: {self.cache_dir.absolute()}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        캐시에서 데이터 조회
        
        Args:
            key: 캐시 키
            
        Returns:
            Optional[Any]: 캐시된 데이터 (없거나 만료된 경우 None)
        """
        cache_file = self._get_cache_file_path(key)
        
        if not cache_file.exists():
            logger.debug(f"캐시 미스: {key}")
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # 만료 시간 확인
            expired_at = datetime.fromisoformat(cache_data['expired_at'])
            if datetime.now() > expired_at:
                logger.debug(f"캐시 만료: {key}")
                # 만료된 캐시 파일 삭제
                cache_file.unlink()
                return None
            
            logger.debug(f"캐시 히트: {key}")
            return cache_data['data']
            
        except Exception as e:
            logger.warning(f"캐시 읽기 실패: {key}, 오류: {e}")
            return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """
        캐시에 데이터 저장
        
        Args:
            key: 캐시 키
            data: 저장할 데이터
            ttl: Time To Live (초 단위, None이면 기본값 사용)
            
        Returns:
            bool: 저장 성공 여부
        """
        if ttl is None:
            ttl = self.default_ttl
        
        cache_file = self._get_cache_file_path(key)
        
        try:
            # 만료 시간 계산
            expired_at = datetime.now() + timedelta(seconds=ttl)
            
            cache_data = {
                'key': key,
                'data': data,
                'created_at': datetime.now().isoformat(),
                'expired_at': expired_at.isoformat(),
                'ttl': ttl
            }
            
            # 캐시 파일 저장
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"캐시 저장: {key} (TTL: {ttl}초)")
            return True
            
        except Exception as e:
            logger.error(f"캐시 저장 실패: {key}, 오류: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        캐시 삭제
        
        Args:
            key: 캐시 키
            
        Returns:
            bool: 삭제 성공 여부
        """
        cache_file = self._get_cache_file_path(key)
        
        try:
            if cache_file.exists():
                cache_file.unlink()
                logger.debug(f"캐시 삭제: {key}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"캐시 삭제 실패: {key}, 오류: {e}")
            return False
    
    def clear_all(self) -> int:
        """
        모든 캐시 삭제
        
        Returns:
            int: 삭제된 캐시 파일 수
        """
        count = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1
            
            logger.info(f"전체 캐시 삭제 완료: {count}개")
            return count
            
        except Exception as e:
            logger.error(f"전체 캐시 삭제 실패: {e}")
            return count
    
    def clear_expired(self) -> int:
        """
        만료된 캐시만 삭제
        
        Returns:
            int: 삭제된 캐시 파일 수
        """
        count = 0
        now = datetime.now()
        
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    expired_at = datetime.fromisoformat(cache_data['expired_at'])
                    if now > expired_at:
                        cache_file.unlink()
                        count += 1
                        
                except Exception as e:
                    logger.warning(f"캐시 파일 처리 실패: {cache_file.name}, 오류: {e}")
                    continue
            
            logger.info(f"만료된 캐시 삭제 완료: {count}개")
            return count
            
        except Exception as e:
            logger.error(f"만료된 캐시 삭제 실패: {e}")
            return count
    
    def get_cache_info(self, key: str) -> Optional[Dict]:
        """
        캐시 메타데이터 조회
        
        Args:
            key: 캐시 키
            
        Returns:
            Optional[Dict]: 캐시 메타데이터 (생성 시간, 만료 시간 등)
        """
        cache_file = self._get_cache_file_path(key)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            return {
                'key': cache_data['key'],
                'created_at': cache_data['created_at'],
                'expired_at': cache_data['expired_at'],
                'ttl': cache_data['ttl'],
                'is_expired': datetime.now() > datetime.fromisoformat(cache_data['expired_at'])
            }
            
        except Exception as e:
            logger.warning(f"캐시 정보 조회 실패: {key}, 오류: {e}")
            return None
    
    def _get_cache_file_path(self, key: str) -> Path:
        """
        캐시 키로부터 파일 경로 생성
        
        Args:
            key: 캐시 키
            
        Returns:
            Path: 캐시 파일 경로
        """
        # 키를 해시하여 파일명 생성 (특수문자 방지)
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    def get_or_set(self, key: str, fetch_func, ttl: Optional[int] = None) -> Any:
        """
        캐시에서 데이터 조회, 없으면 fetch_func 실행 후 저장
        
        Args:
            key: 캐시 키
            fetch_func: 데이터를 가져오는 함수
            ttl: Time To Live (초 단위)
            
        Returns:
            Any: 캐시된 데이터 또는 새로 가져온 데이터
        """
        # 캐시 조회
        cached_data = self.get(key)
        if cached_data is not None:
            return cached_data
        
        # 캐시 미스 - 데이터 가져오기
        try:
            data = fetch_func()
            self.set(key, data, ttl)
            return data
        except Exception as e:
            logger.error(f"데이터 가져오기 실패: {key}, 오류: {e}")
            raise
    
    def get_cache_stats(self) -> Dict:
        """
        캐시 통계 정보 조회
        
        Returns:
            Dict: 캐시 통계 (전체 개수, 만료된 개수, 총 크기 등)
        """
        total_count = 0
        expired_count = 0
        total_size = 0
        now = datetime.now()
        
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                total_count += 1
                total_size += cache_file.stat().st_size
                
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    expired_at = datetime.fromisoformat(cache_data['expired_at'])
                    if now > expired_at:
                        expired_count += 1
                        
                except Exception:
                    continue
            
            return {
                'total_count': total_count,
                'expired_count': expired_count,
                'active_count': total_count - expired_count,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"캐시 통계 조회 실패: {e}")
            return {
                'total_count': 0,
                'expired_count': 0,
                'active_count': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0
            }
