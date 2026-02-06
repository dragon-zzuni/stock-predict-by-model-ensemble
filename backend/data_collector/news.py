"""
뉴스 수집 및 감성 분석 모듈
"""
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from loguru import logger
import asyncio
from textblob import TextBlob

from config import settings


class NewsCollector:
    """뉴스 수집 및 감성 분석 클래스"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        초기화
        
        Args:
            api_key: News API 키 (환경 변수에서 자동 로드)
        """
        self.api_key = api_key or settings.news_api_key
        # 무료 플랜에서는 top-headlines만 사용 가능
        self.base_url = "https://newsapi.org/v2/top-headlines"
        self.max_months = 6  # 최근 6개월 (실제로는 최신 헤드라인만 가져옴)
        self.max_results = 50  # 최대 뉴스 개수
        
    async def fetch_and_analyze(self, symbol: str, company_name: str = "") -> Dict:
        """
        뉴스 수집 및 감성 분석
        
        Args:
            symbol: 종목 코드
            company_name: 회사명 (검색 쿼리 개선용)
            
        Returns:
            Dict: {
                'news_summary': str,
                'sentiment_score': float,
                'news_count': int,
                'articles': List[Dict]
            }
        """
        try:
            # 비동기 실행
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._fetch_and_analyze_sync, 
                symbol, 
                company_name
            )
            return result
            
        except Exception as e:
            logger.error(f"뉴스 수집 실패 - 종목: {symbol}, 오류: {e}")
            # 실패 시 기본값 반환
            return {
                'news_summary': '뉴스 데이터를 가져올 수 없습니다.',
                'sentiment_score': 0.0,
                'news_count': 0,
                'articles': []
            }
    
    def _fetch_and_analyze_sync(self, symbol: str, company_name: str) -> Dict:
        """
        동기 방식으로 뉴스 수집 및 분석
        
        Args:
            symbol: 종목 코드
            company_name: 회사명
            
        Returns:
            Dict: 뉴스 및 감성 분석 결과
        """
        # API 키가 없으면 더미 데이터 반환
        if not self.api_key:
            logger.warning("News API 키가 설정되지 않았습니다. 더미 데이터를 반환합니다.")
            return self._get_dummy_news_data(symbol, company_name)
        
        # 검색 쿼리 생성
        query = self._build_search_query(symbol, company_name)
        
        # top-headlines는 날짜 범위를 지원하지 않음 (최신 헤드라인만)
        # 대신 카테고리와 국가를 지정할 수 있음
        
        # API 요청 파라미터 (무료 플랜용)
        params = {
            'q': query,
            'language': 'en',  # 영어 뉴스 (감성 분석 정확도 향상)
            'sortBy': 'publishedAt',  # 최신순
            'pageSize': min(self.max_results, 100),  # top-headlines는 최대 100개
            'apiKey': self.api_key
        }
        
        logger.info(f"뉴스 수집 시작 (top-headlines): {query}")
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] != 'ok':
                error_msg = data.get('message', 'Unknown error')
                logger.error(f"News API 오류: {error_msg}")
                # API 오류 시 더미 데이터 반환
                return self._get_dummy_news_data(symbol, company_name)
            
            articles = data.get('articles', [])
            
            if not articles:
                logger.warning(f"뉴스를 찾을 수 없습니다: {query}")
                return {
                    'news_summary': '관련 뉴스를 찾을 수 없습니다.',
                    'sentiment_score': 0.0,
                    'news_count': 0,
                    'articles': []
                }
            
            # 감성 분석 수행
            sentiment_results = self._analyze_sentiment(articles)
            
            # 뉴스 요약 생성
            summary = self._generate_summary(articles, sentiment_results)
            
            logger.info(
                f"뉴스 수집 완료: {len(articles)}개, "
                f"감성 점수: {sentiment_results['average_score']:.2f}"
            )
            
            return {
                'news_summary': summary,
                'sentiment_score': sentiment_results['average_score'],
                'news_count': len(articles),
                'articles': articles[:10]  # 상위 10개만 저장
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"News API 요청 실패: {e}")
            return self._get_dummy_news_data(symbol, company_name)
    
    def _build_search_query(self, symbol: str, company_name: str) -> str:
        """
        검색 쿼리 생성
        
        Args:
            symbol: 종목 코드
            company_name: 회사명
            
        Returns:
            str: 검색 쿼리
        """
        # 회사명이 있으면 우선 사용
        if company_name:
            return f'"{company_name}" OR {symbol}'
        
        # 종목 코드만 사용
        return symbol
    
    def _analyze_sentiment(self, articles: List[Dict]) -> Dict:
        """
        뉴스 감성 분석
        
        Args:
            articles: 뉴스 기사 리스트
            
        Returns:
            Dict: {
                'average_score': float,
                'positive_count': int,
                'negative_count': int,
                'neutral_count': int
            }
        """
        sentiments = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for article in articles:
            # 제목과 설명을 결합하여 분석
            text = f"{article.get('title', '')} {article.get('description', '')}"
            
            if not text.strip():
                continue
            
            # TextBlob을 사용한 감성 분석
            try:
                blob = TextBlob(text)
                polarity = blob.sentiment.polarity  # -1.0 ~ 1.0
                sentiments.append(polarity)
                
                # 분류
                if polarity > 0.1:
                    positive_count += 1
                elif polarity < -0.1:
                    negative_count += 1
                else:
                    neutral_count += 1
                    
            except Exception as e:
                logger.warning(f"감성 분석 실패: {e}")
                continue
        
        # 평균 감성 점수 계산
        average_score = sum(sentiments) / len(sentiments) if sentiments else 0.0
        
        return {
            'average_score': average_score,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_analyzed': len(sentiments)
        }
    
    def _generate_summary(self, articles: List[Dict], sentiment_results: Dict) -> str:
        """
        뉴스 요약 생성
        
        Args:
            articles: 뉴스 기사 리스트
            sentiment_results: 감성 분석 결과
            
        Returns:
            str: 뉴스 요약문
        """
        total = sentiment_results['total_analyzed']
        positive = sentiment_results['positive_count']
        negative = sentiment_results['negative_count']
        neutral = sentiment_results['neutral_count']
        avg_score = sentiment_results['average_score']
        
        # 감성 판단
        if avg_score > 0.2:
            sentiment_label = "긍정적"
        elif avg_score < -0.2:
            sentiment_label = "부정적"
        else:
            sentiment_label = "중립적"
        
        # 최근 주요 뉴스 제목 추출 (상위 3개)
        top_headlines = [article.get('title', '') for article in articles[:3]]
        headlines_text = "\n".join([f"- {title}" for title in top_headlines if title])
        
        summary = f"""최근 {len(articles)}개의 헤드라인 뉴스가 수집되었습니다.
전체적인 시장 감성은 {sentiment_label}입니다 (긍정: {positive}, 중립: {neutral}, 부정: {negative}).

주요 뉴스:
{headlines_text}
"""
        
        return summary.strip()
    
    def _get_dummy_news_data(self, symbol: str, company_name: str) -> Dict:
        """
        더미 뉴스 데이터 생성 (API 키가 없거나 실패 시)
        
        Args:
            symbol: 종목 코드
            company_name: 회사명
            
        Returns:
            Dict: 더미 뉴스 데이터
        """
        name = company_name or symbol
        
        return {
            'news_summary': f'{name}에 대한 최근 뉴스 데이터를 가져올 수 없습니다. News API 키를 설정해주세요.',
            'sentiment_score': 0.0,
            'news_count': 0,
            'articles': []
        }
    
    def get_sentiment_label(self, score: float) -> str:
        """
        감성 점수를 레이블로 변환
        
        Args:
            score: 감성 점수 (-1.0 ~ 1.0)
            
        Returns:
            str: "긍정" 또는 "부정"
        """
        return "긍정" if score >= 0 else "부정"
