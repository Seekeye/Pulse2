import React from 'react';

const BarChart = ({ data = [], width = 200, height = 100, color = '#3B82F6' }) => {
  if (!data || data.length === 0) {
    return (
      <div 
        className="flex items-center justify-center bg-gray-100 rounded"
        style={{ width, height }}
      >
        <span className="text-xs text-gray-400">No data</span>
      </div>
    );
  }

  const maxValue = Math.max(...data.map(item => item.value));
  const barWidth = width / data.length - 2;
  const maxBarHeight = height - 20;

  return (
    <div className="relative">
      <svg width={width} height={height} className="overflow-visible">
        {data.map((item, index) => {
          const barHeight = (item.value / maxValue) * maxBarHeight;
          const x = index * (barWidth + 2);
          const y = height - barHeight - 10;
          
          return (
            <g key={index}>
              <rect
                x={x}
                y={y}
                width={barWidth}
                height={barHeight}
                fill={item.color || color}
                className="hover:opacity-80 transition-opacity"
                rx="2"
              />
              <text
                x={x + barWidth / 2}
                y={y - 5}
                textAnchor="middle"
                className="text-xs fill-gray-600"
              >
                {item.value}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

export default BarChart;
