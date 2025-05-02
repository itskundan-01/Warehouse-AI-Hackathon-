import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { 
  Box, 
  Drawer, 
  AppBar, 
  Toolbar, 
  Typography,
  Divider,
  IconButton,
  useMediaQuery,
  useTheme,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Tooltip,
  Badge
} from '@mui/material';
import {
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  Dashboard as DashboardIcon,
  Person as PersonIcon,
  LocalShipping as VehicleIcon,
  Inventory as InventoryIcon,
  Search as SearchIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  Logout as LogoutIcon,
  AdminPanelSettings as AdminIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { toggleSidebar, setSidebarOpen } from '../../store/slices/uiSlice';
import { logout } from '../../store/slices/authSlice';

// Constants
const DRAWER_WIDTH = 240;

const MainLayout = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const dispatch = useDispatch();
  const navigate = useNavigate();
  
  // Get sidebar state from Redux store
  const { sidebarOpen } = useSelector(state => state.ui);
  const { user } = useSelector(state => state.auth);
  
  // State for user menu
  const [anchorEl, setAnchorEl] = useState(null);
  const [notificationAnchor, setNotificationAnchor] = useState(null);
  
  // Mock notifications for UI demo
  const notifications = [
    { id: 1, message: 'Unauthorized access detected at Gate 3', read: false, time: '5 min ago' },
    { id: 2, message: 'New vehicle registered: KA-01-AB-1234', read: false, time: '15 min ago' },
    { id: 3, message: 'Gunny bag count update: 500 bags processed', read: true, time: '1 hour ago' }
  ];
  
  // Handle drawer open/close
  const handleDrawerToggle = () => {
    dispatch(toggleSidebar());
  };
  
  // Handle closing the drawer in mobile view when navigating
  const handleNavigation = (path) => {
    navigate(path);
    if (isMobile) {
      dispatch(setSidebarOpen(false));
    }
  };
  
  // Handle user menu
  const handleUserMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };
  
  const handleUserMenuClose = () => {
    setAnchorEl(null);
  };
  
  // Handle notifications menu
  const handleNotificationOpen = (event) => {
    setNotificationAnchor(event.currentTarget);
  };
  
  const handleNotificationClose = () => {
    setNotificationAnchor(null);
  };
  
  // Handle logout
  const handleLogout = () => {
    handleUserMenuClose();
    dispatch(logout());
    navigate('/login');
  };
  
  const userMenuOpen = Boolean(anchorEl);
  const notificationsOpen = Boolean(notificationAnchor);
  
  // Navigation items
  const navigationItems = [
    { 
      name: 'Dashboard', 
      path: '/dashboard', 
      icon: <DashboardIcon /> 
    },
    { 
      name: 'Facial Recognition', 
      path: '/facial-recognition', 
      icon: <PersonIcon /> 
    },
    { 
      name: 'Vehicle Recognition', 
      path: '/vehicle-recognition', 
      icon: <VehicleIcon /> 
    },
    { 
      name: 'Gunny Counter', 
      path: '/gunny-counter', 
      icon: <InventoryIcon /> 
    },
    { 
      name: 'Contextual Intelligence', 
      path: '/contextual-intelligence', 
      icon: <SearchIcon /> 
    }
  ];
  
  // If user is admin, add admin panel
  if (user?.role === 'admin') {
    navigationItems.push({
      name: 'Admin Panel',
      path: '/admin',
      icon: <AdminIcon />
    });
  }
  
  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* App Bar */}
      <AppBar 
        position="fixed" 
        sx={{ 
          zIndex: theme.zIndex.drawer + 1,
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          ...(sidebarOpen && {
            marginLeft: DRAWER_WIDTH,
            width: `calc(100% - ${DRAWER_WIDTH}px)`,
            transition: theme.transitions.create(['width', 'margin'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.enteringScreen,
            }),
          }),
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            {sidebarOpen ? <ChevronLeftIcon /> : <MenuIcon />}
          </IconButton>
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            WarehouseVision AI
          </Typography>
          
          {/* Notifications */}
          <Box sx={{ display: 'flex' }}>
            <Tooltip title="Notifications">
              <IconButton 
                color="inherit"
                onClick={handleNotificationOpen}
              >
                <Badge 
                  badgeContent={notifications.filter(n => !n.read).length} 
                  color="error"
                >
                  <NotificationsIcon />
                </Badge>
              </IconButton>
            </Tooltip>
            
            {/* User menu */}
            <Tooltip title="Account settings">
              <IconButton
                onClick={handleUserMenuOpen}
                size="small"
                aria-controls={userMenuOpen ? 'account-menu' : undefined}
                aria-haspopup="true"
                aria-expanded={userMenuOpen ? 'true' : undefined}
                sx={{ ml: 1 }}
              >
                <Avatar 
                  sx={{ 
                    width: 32, 
                    height: 32, 
                    bgcolor: theme.palette.primary.main 
                  }}
                >
                  {user?.name?.charAt(0) || 'U'}
                </Avatar>
              </IconButton>
            </Tooltip>
          </Box>
          
          {/* User dropdown menu */}
          <Menu
            id="account-menu"
            anchorEl={anchorEl}
            open={userMenuOpen}
            onClose={handleUserMenuClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            <Box sx={{ px: 2, py: 1 }}>
              <Typography variant="subtitle1">{user?.name || 'User'}</Typography>
              <Typography variant="body2" color="text.secondary">
                {user?.email || 'user@example.com'}
              </Typography>
            </Box>
            <Divider />
            <MenuItem onClick={() => {
              handleUserMenuClose();
              navigate('/profile');
            }}>
              <ListItemIcon>
                <PersonIcon fontSize="small" />
              </ListItemIcon>
              Profile
            </MenuItem>
            <MenuItem onClick={() => {
              handleUserMenuClose();
              navigate('/settings');
            }}>
              <ListItemIcon>
                <SettingsIcon fontSize="small" />
              </ListItemIcon>
              Settings
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
          
          {/* Notifications menu */}
          <Menu
            id="notifications-menu"
            anchorEl={notificationAnchor}
            open={notificationsOpen}
            onClose={handleNotificationClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            PaperProps={{
              sx: {
                width: 320,
                maxHeight: 400,
              }
            }}
          >
            <Box sx={{ px: 2, py: 1, display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="subtitle1">Notifications</Typography>
              <Typography 
                variant="body2" 
                color="primary" 
                sx={{ cursor: 'pointer' }}
                onClick={handleNotificationClose}
              >
                Mark all as read
              </Typography>
            </Box>
            <Divider />
            {notifications.length === 0 ? (
              <Box sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  No notifications
                </Typography>
              </Box>
            ) : (
              notifications.map((notification) => (
                <MenuItem 
                  key={notification.id}
                  sx={{ 
                    backgroundColor: notification.read ? 'inherit' : 'rgba(25, 118, 210, 0.08)',
                    whiteSpace: 'normal',
                  }}
                  onClick={handleNotificationClose}
                >
                  <Box sx={{ width: '100%' }}>
                    <Typography variant="body2">{notification.message}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {notification.time}
                    </Typography>
                  </Box>
                </MenuItem>
              ))
            )}
            <Divider />
            <Box sx={{ p: 1, textAlign: 'center' }}>
              <Typography 
                variant="body2" 
                color="primary" 
                sx={{ cursor: 'pointer' }}
                onClick={() => {
                  handleNotificationClose();
                  navigate('/notifications');
                }}
              >
                View all notifications
              </Typography>
            </Box>
          </Menu>
        </Toolbar>
      </AppBar>
      
      {/* Sidebar */}
      <Drawer
        variant={isMobile ? "temporary" : "permanent"}
        open={sidebarOpen}
        onClose={isMobile ? handleDrawerToggle : undefined}
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            ...(isMobile ? {} : {
              position: 'relative',
              whiteSpace: 'nowrap',
              overflowX: 'hidden',
              transition: theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
              }),
              width: sidebarOpen ? DRAWER_WIDTH : theme.spacing(7),
              [theme.breakpoints.up('sm')]: {
                width: sidebarOpen ? DRAWER_WIDTH : theme.spacing(9),
              },
            })
          },
        }}
      >
        <Toolbar />
        <Box sx={{ overflow: 'auto', mt: 2 }}>
          <List>
            {navigationItems.map((item) => (
              <ListItem 
                button 
                key={item.name}
                onClick={() => handleNavigation(item.path)}
                sx={{
                  minHeight: 48,
                  px: 2.5,
                  justifyContent: sidebarOpen ? 'initial' : 'center',
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 0,
                    mr: sidebarOpen ? 2 : 'auto',
                    justifyContent: 'center',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.name} 
                  sx={{ 
                    display: sidebarOpen ? 'block' : 'none',
                    whiteSpace: 'nowrap'
                  }} 
                />
              </ListItem>
            ))}
          </List>
          <Divider sx={{ my: 1 }} />
          <List>
            <ListItem 
              button 
              onClick={handleLogout}
              sx={{
                minHeight: 48,
                px: 2.5,
                justifyContent: sidebarOpen ? 'initial' : 'center',
              }}
            >
              <ListItemIcon
                sx={{
                  minWidth: 0,
                  mr: sidebarOpen ? 2 : 'auto',
                  justifyContent: 'center',
                }}
              >
                <LogoutIcon />
              </ListItemIcon>
              <ListItemText 
                primary="Logout" 
                sx={{ 
                  display: sidebarOpen ? 'block' : 'none',
                  whiteSpace: 'nowrap'
                }} 
              />
            </ListItem>
          </List>
        </Box>
      </Drawer>
      
      {/* Main Content */}
      <Box 
        component="main" 
        sx={{ 
          flexGrow: 1, 
          p: 3,
          overflow: 'auto',
          backgroundColor: theme.palette.background.default,
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column' 
        }}
      >
        <Toolbar /> {/* This acts as a spacer to push content below the AppBar */}
        <Box 
          sx={{ 
            flexGrow: 1,
            py: 1,
            width: '100%'
          }}
        >
          <Outlet />
        </Box>
        
        {/* Footer */}
        <Box 
          component="footer" 
          sx={{ 
            mt: 'auto', 
            py: 2,
            textAlign: 'center',
            borderTop: `1px solid ${theme.palette.divider}`,
          }}
        >
          <Typography variant="body2" color="text.secondary">
            © {new Date().getFullYear()} WarehouseVision AI | All Rights Reserved
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default MainLayout;