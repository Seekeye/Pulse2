import React from 'react'
import { motion } from 'framer-motion'

const ScrollStack = ({ children, className = "" }) => {
  return (
    <div className={`relative ${className}`}>
      <div className="flex flex-col space-y-4">
        {React.Children.map(children, (child, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ 
              duration: 0.6, 
              delay: index * 0.1,
              ease: "easeOut"
            }}
            viewport={{ once: true, margin: "-100px" }}
            className="relative"
          >
            {child}
          </motion.div>
        ))}
      </div>
    </div>
  )
}

export default ScrollStack

