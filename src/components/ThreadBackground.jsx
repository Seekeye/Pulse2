import { motion } from 'framer-motion'

const ThreadBackground = () => {
  return (
    <div className="absolute inset-0 overflow-hidden">
      {/* Thread 1 */}
      <motion.div
        className="absolute top-1/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-electric-blue/30 to-transparent"
        initial={{ x: '-100%' }}
        animate={{ x: '100%' }}
        transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
      />
      
      {/* Thread 2 */}
      <motion.div
        className="absolute top-1/2 left-0 w-full h-px bg-gradient-to-r from-transparent via-electric-blue/20 to-transparent"
        initial={{ x: '100%' }}
        animate={{ x: '-100%' }}
        transition={{ duration: 12, repeat: Infinity, ease: 'linear' }}
      />
      
      {/* Thread 3 */}
      <motion.div
        className="absolute top-3/4 left-0 w-full h-px bg-gradient-to-r from-transparent via-electric-blue/10 to-transparent"
        initial={{ x: '-100%' }}
        animate={{ x: '100%' }}
        transition={{ duration: 15, repeat: Infinity, ease: 'linear' }}
      />
      
      {/* Floating Orbs */}
      <motion.div
        className="absolute top-1/4 left-1/4 w-32 h-32 bg-electric-blue/5 rounded-full blur-xl"
        animate={{
          y: [0, -20, 0],
          x: [0, 10, 0],
        }}
        transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
      />
      
      <motion.div
        className="absolute bottom-1/4 right-1/4 w-24 h-24 bg-electric-blue/10 rounded-full blur-xl"
        animate={{
          y: [0, 15, 0],
          x: [0, -10, 0],
        }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
      />
    </div>
  )
}

export default ThreadBackground