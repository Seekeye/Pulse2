import React from 'react';

const HorizontalBarChart = ({ data = [], width = 200, height = 100, color = '#3B82F6' }) => {
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
  const barHeight = height / data.length - 2;
  const maxBarWidth = width - 40; // Leave space for labels

  return (
    <div className="relative">
      <svg width={width} height={height} className="overflow-visible">
        {data.map((item, index) => {
          const barWidth = (item.value / maxValue) * maxBarWidth;
          const x = 0;
          const y = index * (barHeight + 2);
          
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
                x={barWidth + 5}
                y={y + barHeight / 2}
                textAnchor="start"
                className="text-xs fill-gray-600"
                dominantBaseline="middle"
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

export default HorizontalBarChart;
