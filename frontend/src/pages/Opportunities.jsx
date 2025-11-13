import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  LocationOn as LocationIcon,
  AttachMoney as MoneyIcon,
  Star as StarIcon,
} from '@mui/icons-material';
import { getInvestmentOpportunities } from '../services/api';

function Opportunities() {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [minScore, setMinScore] = useState(70);

  useEffect(() => {
    fetchOpportunities();
  }, []);

  const fetchOpportunities = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getInvestmentOpportunities({ min_score: minScore, limit: 25 });
      setOpportunities(data.opportunities || []);
    } catch (err) {
      setError(err.message || 'Failed to load opportunities');
      // Set mock data for demonstration
      setOpportunities([
        {
          id: '1',
          address: '123 Main St, Atlanta',
          county: 'Fulton',
          price: 450000,
          investment_score: 92,
          cap_rate: 9.5,
          monthly_cash_flow: 2500,
          estimated_value: 520000,
          roi: 15.6,
        },
        {
          id: '2',
          address: '456 Oak Ave, Decatur',
          county: 'DeKalb',
          price: 425000,
          investment_score: 87,
          cap_rate: 8.8,
          monthly_cash_flow: 2200,
          estimated_value: 480000,
          roi: 12.9,
        },
        {
          id: '3',
          address: '789 Pine Rd, Marietta',
          county: 'Cobb',
          price: 395000,
          investment_score: 83,
          cap_rate: 8.2,
          monthly_cash_flow: 1950,
          estimated_value: 445000,
          roi: 12.7,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleMinScoreChange = (event) => {
    setMinScore(event.target.value);
  };

  const applyFilter = () => {
    fetchOpportunities();
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'success';
    if (score >= 80) return 'info';
    if (score >= 70) return 'warning';
    return 'default';
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
          Investment Opportunities
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Top-rated 4-plex investment opportunities based on AI analysis
        </Typography>
      </Box>

      {error && (
        <Alert severity="info" sx={{ mb: 3 }}>
          {error} (Showing sample data)
        </Alert>
      )}

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={6} md={4}>
            <FormControl fullWidth>
              <InputLabel>Minimum Investment Score</InputLabel>
              <Select
                value={minScore}
                label="Minimum Investment Score"
                onChange={handleMinScoreChange}
              >
                <MenuItem value={60}>60+</MenuItem>
                <MenuItem value={70}>70+</MenuItem>
                <MenuItem value={80}>80+</MenuItem>
                <MenuItem value={90}>90+</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={4}>
            <Button variant="contained" onClick={applyFilter} fullWidth>
              Apply Filter
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Opportunities Grid */}
      {opportunities.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary">
            No investment opportunities found
          </Typography>
          <Typography variant="body2" color="text.secondary" mt={1}>
            Try adjusting your filters or start a new discovery job
          </Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {opportunities.map((opportunity) => (
            <Grid item xs={12} md={6} lg={4} key={opportunity.id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Chip
                      icon={<StarIcon />}
                      label={`Score: ${opportunity.investment_score}`}
                      color={getScoreColor(opportunity.investment_score)}
                    />
                    <Chip
                      icon={<LocationIcon />}
                      label={opportunity.county}
                      variant="outlined"
                      size="small"
                    />
                  </Box>

                  <Typography variant="h6" gutterBottom>
                    {opportunity.address}
                  </Typography>

                  <Box mt={2}>
                    <Grid container spacing={1}>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Purchase Price
                        </Typography>
                        <Typography variant="body1" fontWeight="bold">
                          ${opportunity.price?.toLocaleString()}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Estimated Value
                        </Typography>
                        <Typography variant="body1" fontWeight="bold">
                          ${opportunity.estimated_value?.toLocaleString()}
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          Cap Rate
                        </Typography>
                        <Typography variant="body1" fontWeight="bold" color="success.main">
                          {opportunity.cap_rate}%
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="text.secondary">
                          ROI
                        </Typography>
                        <Typography variant="body1" fontWeight="bold" color="success.main">
                          {opportunity.roi}%
                        </Typography>
                      </Grid>
                      <Grid item xs={12}>
                        <Typography variant="caption" color="text.secondary">
                          Monthly Cash Flow
                        </Typography>
                        <Typography variant="body1" fontWeight="bold">
                          ${opportunity.monthly_cash_flow?.toLocaleString()}/mo
                        </Typography>
                      </Grid>
                    </Grid>
                  </Box>
                </CardContent>
                <CardActions>
                  <Button size="small" color="primary">
                    View Details
                  </Button>
                  <Button size="small" color="secondary">
                    Request Analysis
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}

export default Opportunities;
