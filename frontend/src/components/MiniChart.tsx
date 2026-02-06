/**
 * 미니 차트 컴포넌트
 * Canvas를 사용하여 스파크라인 형태의 간단한 가격 추이 차트를 렌더링
 */

import React, { useEffect, useRef } from 'react';

interface MiniChartProps {
  /** 차트에 표시할 가격 데이터 배열 */
  data: number[];
  /** 차트 너비 (픽셀) */
  width?: number;
  /** 차트 높이 (픽셀) */
  height?: number;
  /** 선 색상 */
  color?: string;
  /** 선 두께 */
  lineWidth?: number;
}

/**
 * 미니 차트 컴포넌트
 * 최근 가격 추이를 간단한 선 그래프로 표시
 */
export const MiniChart: React.FC<MiniChartProps> = ({
  data,
  width = 100,
  height = 30,
  color = '#3b82f6',
  lineWidth = 1.5,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !data || data.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 캔버스 초기화
    ctx.clearRect(0, 0, width, height);

    // 데이터가 1개 이하면 그리지 않음
    if (data.length <= 1) return;

    // 데이터 정규화
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1; // 0으로 나누기 방지

    // 좌표 계산
    const points = data.map((value, index) => ({
      x: (index / (data.length - 1)) * width,
      y: height - ((value - min) / range) * height,
    }));

    // 선 그리기
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';

    points.forEach((point, index) => {
      if (index === 0) {
        ctx.moveTo(point.x, point.y);
      } else {
        ctx.lineTo(point.x, point.y);
      }
    });

    ctx.stroke();
  }, [data, width, height, color, lineWidth]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className="inline-block"
      aria-label="가격 추이 차트"
    />
  );
};
