import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Button,
  Chip,
} from '@mui/material';
import {
  Home as HomeIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { getDashboardAnalytics, getHealthStatus } from '../services/api';

function Dashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [analyticsData, healthData] = await Promise.allSettled([
        getDashboardAnalytics(),
        getHealthStatus(),
      ]);

      if (analyticsData.status === 'fulfilled') {
        setAnalytics(analyticsData.value);
      }

      if (healthData.status === 'fulfilled') {
        setHealth(healthData.value);
      }
    } catch (err) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box mb={3}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Welcome to the 4-Plex Unified Investment Platform
        </Typography>
      </Box>

      {error && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* System Health Status */}
      {health && (
        <Box mb={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="h6">System Status</Typography>
                <Chip
                  icon={<CheckCircleIcon />}
                  label={health.status || 'Unknown'}
                  color={health.status === 'healthy' ? 'success' : 'error'}
                />
              </Box>
              <Typography variant="caption" color="text.secondary">
                Last updated: {health.timestamp || 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Main Metrics */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 140,
            }}
          >
            <Box display="flex" alignItems="center" mb={1}>
              <HomeIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6" component="div">
                Properties
              </Typography>
            </Box>
            <Typography variant="h3" component="div" sx={{ flexGrow: 1 }}>
              {analytics?.total_properties || '0'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Total discovered
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 140,
            }}
          >
            <Box display="flex" alignItems="center" mb={1}>
              <AssessmentIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6" component="div">
                Analyzed
              </Typography>
            </Box>
            <Typography variant="h3" component="div" sx={{ flexGrow: 1 }}>
              {analytics?.analyzed_properties || '0'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Completed analyses
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 140,
            }}
          >
            <Box display="flex" alignItems="center" mb={1}>
              <TrendingUpIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6" component="div">
                Opportunities
              </Typography>
            </Box>
            <Typography variant="h3" component="div" sx={{ flexGrow: 1 }}>
              {analytics?.high_score_properties || '0'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              High-value investments
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 140,
            }}
          >
            <Box display="flex" alignItems="center" mb={1}>
              <CheckCircleIcon color="primary" sx={{ mr: 1 }} />
              <Typography variant="h6" component="div">
                Avg Score
              </Typography>
            </Box>
            <Typography variant="h3" component="div" sx={{ flexGrow: 1 }}>
              {analytics?.average_score || 'N/A'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Investment score
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Box mb={3}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Box display="flex" gap={2} flexWrap="wrap">
              <Button variant="contained" color="primary" href="/properties">
                View Properties
              </Button>
              <Button variant="contained" color="secondary" href="/opportunities">
                Investment Opportunities
              </Button>
              <Button variant="outlined" color="primary" href="/analytics">
                View Analytics
              </Button>
              <Button variant="outlined" onClick={fetchDashboardData}>
                Refresh Data
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Recent Activity */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Discovery Status
              </Typography>
              <Typography variant="body2" color="text.secondary">
                AI agents are continuously monitoring 5 Georgia counties for 4-plex investment opportunities.
              </Typography>
              <Box mt={2}>
                <Typography variant="caption" display="block">
                  Target Counties: Fulton, DeKalb, Clayton, Cobb, Atlanta
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Platform Features
              </Typography>
              <Typography variant="body2" color="text.secondary" component="div">
                <ul style={{ paddingLeft: '20px', marginTop: '10px' }}>
                  <li>24/7 AI-powered property discovery</li>
                  <li>Professional investment analysis</li>
                  <li>Cap rate and cash flow calculations</li>
                  <li>Risk assessment and scoring</li>
                  <li>Real-time opportunity alerts</li>
                </ul>
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
