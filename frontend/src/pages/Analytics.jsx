import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
} from '@mui/material';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { getCountyAnalytics, getPerformanceMetrics } from '../services/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

function Analytics() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [countyData, setCountyData] = useState(null);
  const [performanceData, setPerformanceData] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);

      const [county, performance] = await Promise.allSettled([
        getCountyAnalytics(),
        getPerformanceMetrics(),
      ]);

      if (county.status === 'fulfilled') {
        setCountyData(county.value);
      }

      if (performance.status === 'fulfilled') {
        setPerformanceData(performance.value);
      }

      // Set mock data for demonstration
      setCountyData([
        { county: 'Fulton', properties: 45, avg_score: 82, total_value: 21000000 },
        { county: 'DeKalb', properties: 38, avg_score: 78, total_value: 16500000 },
        { county: 'Clayton', properties: 32, avg_score: 74, total_value: 12200000 },
        { county: 'Cobb', properties: 28, avg_score: 76, total_value: 13800000 },
        { county: 'Atlanta', properties: 25, avg_score: 85, total_value: 14500000 },
      ]);

      setPerformanceData({
        discovery_rate: [
          { month: 'Jul', count: 45 },
          { month: 'Aug', count: 62 },
          { month: 'Sep', count: 58 },
          { month: 'Oct', count: 71 },
          { month: 'Nov', count: 68 },
        ],
        score_distribution: [
          { range: '90-100', count: 12 },
          { range: '80-89', count: 34 },
          { range: '70-79', count: 56 },
          { range: '60-69', count: 42 },
          { range: '<60', count: 24 },
        ],
        avg_analysis_time: 18.5,
        total_analyzed: 168,
      });
    } catch (err) {
      setError(err.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
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
          Analytics
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Comprehensive analytics and performance metrics
        </Typography>
      </Box>

      {error && (
        <Alert severity="info" sx={{ mb: 3 }}>
          {error} (Showing sample data)
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="County Performance" />
          <Tab label="Discovery Trends" />
          <Tab label="Score Distribution" />
        </Tabs>
      </Box>

      {/* County Performance Tab */}
      {tabValue === 0 && countyData && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Properties by County
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={countyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="county" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="properties" fill="#0088FE" name="Properties" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Average Investment Score by County
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={countyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="county" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="avg_score" fill="#00C49F" name="Avg Score" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Total Property Value by County
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={countyData}
                    dataKey="total_value"
                    nameKey="county"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label={(entry) => `${entry.county}: $${(entry.total_value / 1000000).toFixed(1)}M`}
                  >
                    {countyData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => `$${(value / 1000000).toFixed(2)}M`} />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Discovery Trends Tab */}
      {tabValue === 1 && performanceData && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Monthly Property Discovery Rate
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={performanceData.discovery_rate}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="count"
                    stroke="#8884d8"
                    strokeWidth={2}
                    name="Properties Discovered"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  Total Analyzed
                </Typography>
                <Typography variant="h3">{performanceData.total_analyzed}</Typography>
                <Typography variant="caption" color="text.secondary">
                  Properties
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  Avg Analysis Time
                </Typography>
                <Typography variant="h3">{performanceData.avg_analysis_time}</Typography>
                <Typography variant="caption" color="text.secondary">
                  Minutes
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  Current Month
                </Typography>
                <Typography variant="h3">
                  {performanceData.discovery_rate[performanceData.discovery_rate.length - 1]?.count || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Properties Discovered
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Score Distribution Tab */}
      {tabValue === 2 && performanceData && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Investment Score Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={performanceData.score_distribution}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="range" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" fill="#FFBB28" name="Properties" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Score Distribution (Pie)
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={performanceData.score_distribution}
                    dataKey="count"
                    nameKey="range"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                  >
                    {performanceData.score_distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}

export default Analytics;
