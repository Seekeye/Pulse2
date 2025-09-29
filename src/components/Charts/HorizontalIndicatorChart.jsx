import React from 'react';

const HorizontalIndicatorChart = ({ data = [], width = 200, height = 120 }) => {
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

  const maxValue = 100; // Fixed max value for consistency
  const barHeight = 18;
  const barSpacing = 6;
  const labelWidth = 70;
  const chartWidth = width - labelWidth - 30;

  return (
    <div className="relative" style={{ width, height }}>
      <svg width={width} height={height} className="overflow-visible">
        {/* Scale reference lines */}
        {[0, 25, 50, 75, 100].map((value) => {
          const x = labelWidth + (value / maxValue) * chartWidth;
          return (
            <g key={value}>
              <line
                x1={x}
                y1={5}
                x2={x}
                y2={height - 5}
                stroke="#e5e7eb"
                strokeWidth="1"
                strokeDasharray="2,2"
                opacity="0.5"
              />
              <text
                x={x}
                y={height - 2}
                textAnchor="middle"
                className="text-xs fill-gray-400"
                dominantBaseline="hanging"
              >
                {value}%
              </text>
            </g>
          );
        })}
        
        {data.map((item, index) => {
          const barWidth = (item.value / maxValue) * chartWidth;
          const y = index * (barHeight + barSpacing) + 10;
          
          return (
            <g key={index}>
              {/* Bar background */}
              <rect
                x={labelWidth}
                y={y}
                width={chartWidth}
                height={barHeight}
                fill="#f3f4f6"
                rx="4"
                className="opacity-50"
              />
              {/* Bar fill with gradient effect */}
              <rect
                x={labelWidth}
                y={y}
                width={barWidth}
                height={barHeight}
                fill={item.color || '#3B82F6'}
                className="hover:opacity-90 transition-all duration-200"
                rx="4"
                style={{
                  filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.1))'
                }}
              />
              {/* Label */}
              <text
                x={labelWidth - 8}
                y={y + barHeight / 2}
                textAnchor="end"
                className="text-xs fill-gray-700 font-medium"
                dominantBaseline="middle"
              >
                {item.label}
              </text>
              {/* Value with percentage */}
              <text
                x={labelWidth + barWidth + 8}
                y={y + barHeight / 2}
                textAnchor="start"
                className="text-xs fill-gray-600 font-semibold"
                dominantBaseline="middle"
              >
                {item.value}%
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

export default HorizontalIndicatorChart;
