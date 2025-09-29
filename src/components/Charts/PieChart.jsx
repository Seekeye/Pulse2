import React, { useState } from 'react';

const PieChart = ({ data = [], size = 120, colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444'] }) => {
  const [hoveredSegment, setHoveredSegment] = useState(null);

  if (!data || data.length === 0) {
    return (
      <div 
        className="flex items-center justify-center bg-gray-100 rounded-full"
        style={{ width: size, height: size }}
      >
        <span className="text-xs text-gray-400">No data</span>
      </div>
    );
  }

  const total = data.reduce((sum, item) => sum + item.value, 0);
  let cumulativePercentage = 0;

  const segments = data.map((item, index) => {
    const percentage = (item.value / total) * 100;
    const startAngle = (cumulativePercentage / 100) * 360;
    const endAngle = ((cumulativePercentage + percentage) / 100) * 360;
    
    cumulativePercentage += percentage;

    const radius = size / 2 - 15;
    const centerX = size / 2;
    const centerY = size / 2;

    const startAngleRad = (startAngle - 90) * (Math.PI / 180);
    const endAngleRad = (endAngle - 90) * (Math.PI / 180);

    const x1 = centerX + radius * Math.cos(startAngleRad);
    const y1 = centerY + radius * Math.sin(startAngleRad);
    const x2 = centerX + radius * Math.cos(endAngleRad);
    const y2 = centerY + radius * Math.sin(endAngleRad);

    const largeArcFlag = percentage > 50 ? 1 : 0;

    const pathData = [
      `M ${centerX} ${centerY}`,
      `L ${x1} ${y1}`,
      `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
      'Z'
    ].join(' ');

    return (
      <path
        key={index}
        d={pathData}
        fill={colors[index % colors.length]}
        className="hover:opacity-90 transition-all duration-200 cursor-pointer"
        onMouseEnter={() => setHoveredSegment({ ...item, percentage, index })}
        onMouseLeave={() => setHoveredSegment(null)}
        style={{
          filter: hoveredSegment?.index === index ? 'drop-shadow(0 4px 8px rgba(0,0,0,0.2))' : 'none',
          transform: hoveredSegment?.index === index ? 'scale(1.05)' : 'scale(1)',
          transformOrigin: 'center'
        }}
      />
    );
  });

  return (
    <div className="relative">
      <svg width={size} height={size} className="transform -rotate-90">
        {segments}
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center">
          <div className="text-lg font-bold text-gray-900">{total}</div>
          <div className="text-xs text-gray-500">Total</div>
        </div>
      </div>
      
      {/* Tooltip */}
      {hoveredSegment && (
        <div className="absolute top-0 left-full ml-4 bg-gray-900 text-white px-3 py-2 rounded-lg shadow-lg z-10 min-w-max">
          <div className="text-sm font-medium">{hoveredSegment.label}</div>
          <div className="text-xs text-gray-300">
            {hoveredSegment.value} ({hoveredSegment.percentage.toFixed(1)}%)
          </div>
          <div className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-1 w-2 h-2 bg-gray-900 rotate-45"></div>
        </div>
      )}
    </div>
  );
};

export default PieChart;
