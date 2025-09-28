import React from "react";
import {
  Navbar,
  Collapse,
  Typography,
  IconButton,
} from "@material-tailwind/react";
import { Bars3Icon, XMarkIcon } from "@heroicons/react/24/outline";
import { Link, useLocation } from 'react-router-dom';
import { FiHome, FiTrendingUp, FiPieChart,  FiZap } from 'react-icons/fi';
import { MdAttachMoney } from "react-icons/md";
import { GiMoneyStack } from "react-icons/gi";
import { TfiMoney } from "react-icons/tfi";
import { RiPulseAiFill } from "react-icons/ri";


import LogoImg from '../assets/logo.webp';

function NavList() {
  const location = useLocation();
  
  // Don't show navbar on dashboard
  if (location.pathname === '/dashboard' || location.pathname === '/') {
    return null;
  }
  
  const navItems = [
    { name: 'Home', path: '/home', icon: FiHome },
    { name: 'Why Pulse?', path: '/whypulse', icon: RiPulseAiFill },
    { name: 'Features', path: '/features', icon: FiPieChart },
    { name: 'Pricing', path: '/pricing', icon: TfiMoney },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <ul className="my-2 flex flex-col gap-2 lg:mb-0 lg:mt-0 lg:flex-row lg:items-center lg:gap-6">
      {navItems.map((item) => (
        <Typography
          key={item.name}
          as="li"
          variant="small"
          color="blue-gray"
          className="p-1 font-medium"
        >
          <Link 
            to={item.path} 
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-md transition-all duration-300 border text-sm ${
              isActive(item.path) 
                ? 'text-white bg-blue-500/50 border-blue-500/50 shadow-md' 
                : 'text-gray-400 hover:text-white hover:bg-blue-500/30 border-transparent hover:border-blue-500/50 hover:shadow-sm'
            }`}
          >
            <item.icon className="w-4 h-4" />
            <span>{item.name}</span>
          </Link>
        </Typography>
      ))}
    </ul>
  );
}

export function NavbarSimple() {
  const [openNav, setOpenNav] = React.useState(false);
  const location = useLocation();

  // Don't show navbar on dashboard
  if (location.pathname === '/dashboard' || location.pathname === '/') {
    return null;
  }

  const handleWindowResize = () =>
    window.innerWidth >= 960 && setOpenNav(false);

  React.useEffect(() => {
    window.addEventListener("resize", handleWindowResize);

    return () => {
      window.removeEventListener("resize", handleWindowResize);
    };
  }, []);

  return (
    <Navbar className="mx-auto max-w-screen-xl px-6 py-2 bg-black backdrop-blur-md border-b-2 border-gray-500/70 shadow-lg rounded-b-2xl mt-7">
      <div className="flex items-center justify-between text-gray-300 h-12">
        <Link
          to="/"
          className="flex items-center space-x-2 mr-4 cursor-pointer py-1 hover:opacity-80 transition-opacity duration-300"
        >
          <img src={LogoImg} alt="Pulse.Inc" className="h-11 w-11 object-contain" />
          <Typography
            variant="h6"
            className="font-mono font-bold text-lg text-gray-200 hover:text-white transition-colors duration-300"
          >
            Pulse
          </Typography>
        </Link>
        <div className="hidden lg:block">
          <NavList />
        </div>
        <div className="hidden lg:flex items-center gap-4">
          <Link
            to="/dashboard"
            className="flex items-center space-x-2 px-4 py-1.5 bg-gradient-to-r from-blue-500 to-blue-400 text-white text-sm font-mono font-semibold rounded-md hover:from-blue-400 hover:to-blue-300 transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-blue-500/25 border border-blue-500/30"
          >
            <FiZap className="w-4 h-4" />
            <span>Get Started</span>
          </Link>
        </div>
        <IconButton
          variant="text"
          className="ml-auto h-6 w-6 text-gray-400 hover:text-white hover:bg-gray-800/50 focus:bg-gray-800/50 active:bg-gray-800/50 lg:hidden transition-all duration-300 rounded-lg"
          ripple={false}
          onClick={() => setOpenNav(!openNav)}
        >
          {openNav ? (
            <XMarkIcon className="h-6 w-6" strokeWidth={2} />
          ) : (
            <Bars3Icon className="h-6 w-6" strokeWidth={2} />
          )}
        </IconButton>
      </div>
      <Collapse open={openNav}>
        <div className="lg:hidden">
          <NavList />
          <div className="pt-4">
            <Link
              to="/dashboard"
              className="flex items-center justify-center space-x-2 w-full text-center px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-400 text-white text-base font-mono font-semibold rounded-lg hover:from-blue-400 hover:to-blue-300 transition-all duration-300 border border-blue-500/30 hover:shadow-lg hover:shadow-blue-500/25"
              onClick={() => setOpenNav(false)}
            >
              <FiZap className="w-4 h-4" />
              <span>Get Started</span>
            </Link>
          </div>
        </div>
      </Collapse>
    </Navbar>
  );
}

export default NavbarSimple;