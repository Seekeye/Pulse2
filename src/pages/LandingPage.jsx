import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { AiTwotoneExperiment } from "react-icons/ai";
import { GiCrownedExplosion } from "react-icons/gi";
import { GiConcentrationOrb } from "react-icons/gi";


import { FiZap, FiClock, FiActivity, FiMonitor, FiInfo } from 'react-icons/fi'

const LandingPage = () => {

  return (
    <div className="h-screen bg-black text-white relative overflow-hidden ">
      {/* Main Content */}
      <div className="relative z-10 mt-14">
        {/* Hero Section */}
        <section className="h-screen flex items-start justify-center px-4 sm:px-6 lg:px-8 relative pt-32">
          
          <div className="max-w-4xl mx-auto text-center relative z-10">
            {/* Enhanced Title with marketing phrase */}
            <motion.h1
              initial={{ y: 50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-3xl md:text-5xl font-mono font-bold mb-3"
            >
              <span className="bg-gradient-to-r from-white via-blue-100 to-cyan-200 bg-clip-text text-transparent">
                Feel the Pulse of Trading
              </span>
            </motion.h1>
            
            {/* Enhanced Subtitle */}
            <motion.h2
              initial={{ y: 50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="text-lg md:text-xl font-mono font-semibold text-gray-300 mb-4"
            >
              <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                AI-Powered Intelligence
              </span>
            </motion.h2>
            
            {/* Enhanced Description */}
            <motion.p
              initial={{ y: 50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="text-base md:text-lg text-gray-400 font-mono mb-6 max-w-3xl mx-auto leading-relaxed"
            >
              Advanced AI algorithms that analyze market patterns, generate real-time signals, 
              and manage risk intelligently for cryptocurrency trading.
              <br />
              <span className="text-blue-400 font-semibold">Where technology meets opportunity.</span>
            </motion.p>
            
            {/* Enhanced CTA Buttons */}
            <motion.div
              initial={{ y: 50, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.8 }}
              className="flex flex-col sm:flex-row gap-4 justify-center items-center mt-8 "
            >
              <Link
                to="/dashboard"
                className="group relative px-8 py-3 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl font-mono font-semibold text-white hover:from-blue-600 hover:to-cyan-600 transition-all duration-300 hover:scale-105 hover:shadow-xl hover:shadow-blue-500/25 text-base"
              >
                <span className="flex items-center space-x-2">
                  <span>Initiate Pulse</span>
                  <GiConcentrationOrb className="text-lg group-hover:rotate-12 transition-transform duration-300" />
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-cyan-400 rounded-xl blur opacity-0 group-hover:opacity-30 transition-opacity duration-300 -z-10"></div>
              </Link>
              
              <button className="group px-8 py-3 border border-gray-500 rounded-xl font-mono font-semibold text-gray-300 hover:text-white hover:border-blue-400 transition-all duration-300 hover:bg-gray-800/30 text-base">
                <span className="flex items-center space-x-2">
                  <span>Learn More</span>
                  <FiInfo className="text-lg group-hover:scale-110 transition-transform duration-300" />
                </span>
              </button>
            </motion.div>

            {/* Futuristic Stats */}
            <motion.div
              initial={{ y: 30, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 1.0 }}
              className="grid grid-cols-3 gap-8 max-w-2xl mx-auto mt-20"
            >
              <div className="flex items-center justify-center space-x-3">
                <FiActivity className="w-6 h-6 text-blue-400" />
                <div className="text-2xl font-mono font-bold text-blue-400">99.9%</div>
                <div className="text-xs text-gray-500 font-mono">Uptime</div>
              </div>
              <div className="flex items-center justify-center space-x-3">
                <FiClock className="w-6 h-6 text-cyan-400" />
                <div className="text-2xl font-mono font-bold text-cyan-400">&lt;100ms</div>
                <div className="text-xs text-gray-500 font-mono">Latency</div>
              </div>
              <div className="flex items-center justify-center space-x-3">
                <FiMonitor className="w-6 h-6 text-purple-400" />
                <div className="text-2xl font-mono font-bold text-purple-400">24/7</div>
                <div className="text-xs text-gray-500 font-mono">Monitoring</div>
              </div>
            </motion.div>

            {/* Motivational Quote */}
            <motion.div
              initial={{ y: 30, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.8, delay: 1.2 }}
              className="mt-6 text-center"
            >
              <div className="relative max-w-3xl mx-auto">
                <div className="absolute -top-2 -left-2 w-6 h-6 border-l-2 border-t-2 border-blue-500/50"></div>
                <div className="absolute -bottom-2 -right-2 w-6 h-6 border-r-2 border-b-2 border-blue-500/50"></div>
                <div className="px-8 py-6 bg-gray-900/30 backdrop-blur-sm border border-gray-700/50 rounded-lg">
                  <p className="text-lg font-mono italic text-gray-200 mb-3">
                    "Turning market chaos into calculated success"
                  </p>
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                    <span className="text-sm font-mono text-gray-400">
                      — 0xMinusOne, Lead Developer
                    </span>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                  </div>
                </div>
              </div>
            </motion.div>

            
          </div>
        </section>

      </div>
    </div>
  )
}

export default LandingPage