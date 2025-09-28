import React from 'react';

const VerticalIndicatorChart = ({ data = [], width = 200, height = 200 }) => {
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
  const barWidth = 35; // Narrower bars
  const barSpacing = 15; // Less spacing between bars
  const labelHeight = 25;
  const chartHeight = height - labelHeight - 40;
  const chartWidth = width - 60; // Less space for labels

  return (
    <div className="relative" style={{ width, height }}>
      <svg width={width} height={height} className="overflow-visible">
        
        {data.map((item, index) => {
          const barHeight = (item.value / maxValue) * chartHeight;
          // Center the bars in the available width
          const totalBarsWidth = data.length * barWidth + (data.length - 1) * barSpacing;
          const startX = (width - totalBarsWidth) / 2;
          const x = startX + index * (barWidth + barSpacing);
          const y = labelHeight + chartHeight - barHeight;
          
          return (
            <g key={index}>
              {/* Bar background */}
              <rect
                x={x}
                y={labelHeight}
                width={barWidth}
                height={chartHeight}
                fill="#f3f4f6"
                rx="4"
                className="opacity-50"
              />
              {/* Bar fill with gradient effect */}
              <rect
                x={x}
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
                x={x + barWidth / 2}
                y={labelHeight + chartHeight + 15}
                textAnchor="middle"
                className="text-xs fill-gray-700 font-medium"
                dominantBaseline="hanging"
              >
                {item.label}
              </text>
              {/* Value with percentage */}
              <text
                x={x + barWidth / 2}
                y={y - 5}
                textAnchor="middle"
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

export default VerticalIndicatorChart;
