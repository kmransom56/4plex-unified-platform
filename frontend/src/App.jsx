import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  CssBaseline,
  ThemeProvider,
  createTheme,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Home as HomeIcon,
  Analytics as AnalyticsIcon,
  TrendingUp as OpportunitiesIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import Dashboard from './pages/Dashboard';
import Properties from './pages/Properties';
import Analytics from './pages/Analytics';
import Opportunities from './pages/Opportunities';

const drawerWidth = 240;

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Router>
        <Box sx={{ display: 'flex' }}>
          <CssBaseline />
          <AppBar
            position="fixed"
            sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}
          >
            <Toolbar>
              <HomeIcon sx={{ mr: 2 }} />
              <Typography variant="h6" noWrap component="div">
                4-Plex Unified Investment Platform
              </Typography>
            </Toolbar>
          </AppBar>
          <Drawer
            variant="permanent"
            sx={{
              width: drawerWidth,
              flexShrink: 0,
              '& .MuiDrawer-paper': {
                width: drawerWidth,
                boxSizing: 'border-box',
              },
            }}
          >
            <Toolbar />
            <Box sx={{ overflow: 'auto' }}>
              <List>
                <ListItem disablePadding>
                  <ListItemButton component={Link} to="/">
                    <ListItemIcon>
                      <DashboardIcon />
                    </ListItemIcon>
                    <ListItemText primary="Dashboard" />
                  </ListItemButton>
                </ListItem>
                <ListItem disablePadding>
                  <ListItemButton component={Link} to="/properties">
                    <ListItemIcon>
                      <HomeIcon />
                    </ListItemIcon>
                    <ListItemText primary="Properties" />
                  </ListItemButton>
                </ListItem>
                <ListItem disablePadding>
                  <ListItemButton component={Link} to="/opportunities">
                    <ListItemIcon>
                      <OpportunitiesIcon />
                    </ListItemIcon>
                    <ListItemText primary="Opportunities" />
                  </ListItemButton>
                </ListItem>
                <ListItem disablePadding>
                  <ListItemButton component={Link} to="/analytics">
                    <ListItemIcon>
                      <AnalyticsIcon />
                    </ListItemIcon>
                    <ListItemText primary="Analytics" />
                  </ListItemButton>
                </ListItem>
              </List>
            </Box>
          </Drawer>
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              bgcolor: 'background.default',
              p: 3,
            }}
          >
            <Toolbar />
            <Container maxWidth="xl">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/properties" element={<Properties />} />
                <Route path="/opportunities" element={<Opportunities />} />
                <Route path="/analytics" element={<Analytics />} />
              </Routes>
            </Container>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
