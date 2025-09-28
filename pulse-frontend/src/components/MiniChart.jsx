import React from 'react';

const MiniChart = ({ data = [], width = 60, height = 30, color = '#3B82F6', currentPrice = 0 }) => {
  // Generar datos de ejemplo basados en el precio actual
  const chartData = data.length > 0 ? data : generateSampleData(currentPrice);
  
  if (chartData.length === 0) {
    return (
      <div 
        className="flex items-center justify-center bg-gray-100 rounded"
        style={{ width, height }}
      >
        <span className="text-xs text-gray-400">-</span>
      </div>
    );
  }
  
  const min = Math.min(...chartData);
  const max = Math.max(...chartData);
  const range = max - min || 1;
  
  const points = chartData.map((value, index) => {
    const x = (index / (chartData.length - 1)) * (width - 4);
    const y = height - 2 - ((value - min) / range) * (height - 4);
    return `${x + 2},${y + 1}`;
  }).join(' ');

  // Determinar si la tendencia es alcista o bajista
  const firstPrice = chartData[0];
  const lastPrice = chartData[chartData.length - 1];
  const isPositive = lastPrice >= firstPrice;

  return (
    <div className="relative">
      <svg width={width} height={height} className="overflow-visible">
        {/* Línea de la gráfica */}
        <polyline
          fill="none"
          stroke={color}
          strokeWidth="1.5"
          points={points}
          className="drop-shadow-sm"
        />
        {/* Punto final */}
        <circle
          cx={points.split(' ').pop()?.split(',')[0]}
          cy={points.split(' ').pop()?.split(',')[1]}
          r="1.5"
          fill={color}
        />
        {/* Área bajo la curva (opcional) */}
        <polyline
          fill={`url(#gradient-${isPositive ? 'up' : 'down'})`}
          stroke="none"
          points={`2,${height - 1} ${points} ${width - 2},${height - 1}`}
          opacity="0.1"
        />
        {/* Gradiente */}
        <defs>
          <linearGradient id="gradient-up" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#10B981" stopOpacity="0.3"/>
            <stop offset="100%" stopColor="#10B981" stopOpacity="0"/>
          </linearGradient>
          <linearGradient id="gradient-down" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#EF4444" stopOpacity="0.3"/>
            <stop offset="100%" stopColor="#EF4444" stopOpacity="0"/>
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
};

// Función para generar datos de ejemplo (7-15 días)
const generateSampleData = (currentPrice = 100) => {
  const data = [];
  const basePrice = currentPrice || 100;
  let price = basePrice;
  
  // Generar datos para 10 días (punto medio entre 7-15)
  const days = 10;
  for (let i = 0; i < days; i++) {
    // Cambio más realista por día (0.5% a 3% de volatilidad)
    const dailyVolatility = basePrice * (0.005 + Math.random() * 0.025);
    const trend = (Math.random() - 0.5) * (basePrice * 0.001); // Tendencia muy sutil
    const change = (Math.random() - 0.5) * dailyVolatility + trend;
    
    price = basePrice - (i * (basePrice * 0.0005)) + change; // Tendencia muy sutil hacia abajo
    data.unshift(Math.max(price, basePrice * 0.85)); // No permitir caídas muy grandes
  }
  
  return data;
};

export default MiniChart;
