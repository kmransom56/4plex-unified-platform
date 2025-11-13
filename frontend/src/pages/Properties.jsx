import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  CircularProgress,
  Alert,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
} from '@mui/material';
import { getProperties } from '../services/api';

function Properties() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    county: '',
    min_score: '',
    status: '',
  });

  useEffect(() => {
    fetchProperties();
  }, []);

  const fetchProperties = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {};
      if (filters.county) params.county = filters.county;
      if (filters.min_score) params.min_score = filters.min_score;
      if (filters.status) params.status = filters.status;

      const data = await getProperties(params);
      setProperties(data.properties || []);
    } catch (err) {
      setError(err.message || 'Failed to load properties');
      // Set mock data for demonstration
      setProperties([
        {
          id: '1',
          address: '123 Main St',
          city: 'Atlanta',
          county: 'Fulton',
          price: 450000,
          investment_score: 85,
          status: 'discovered',
          discovery_date: '2025-11-10',
        },
        {
          id: '2',
          address: '456 Oak Ave',
          city: 'Decatur',
          county: 'DeKalb',
          price: 425000,
          investment_score: 78,
          status: 'analyzed',
          discovery_date: '2025-11-11',
        },
        {
          id: '3',
          address: '789 Pine Rd',
          city: 'Jonesboro',
          county: 'Clayton',
          price: 380000,
          investment_score: 72,
          status: 'discovered',
          discovery_date: '2025-11-12',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (field) => (event) => {
    setFilters({
      ...filters,
      [field]: event.target.value,
    });
  };

  const applyFilters = () => {
    fetchProperties();
  };

  const clearFilters = () => {
    setFilters({
      county: '',
      min_score: '',
      status: '',
    });
    fetchProperties();
  };

  const getStatusColor = (status) => {
    const statusColors = {
      discovered: 'info',
      analyzing: 'warning',
      analyzed: 'success',
      rejected: 'error',
    };
    return statusColors[status] || 'default';
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
          Properties
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Browse discovered 4-plex properties across Georgia counties
        </Typography>
      </Box>

      {error && (
        <Alert severity="info" sx={{ mb: 3 }}>
          {error} (Showing sample data)
        </Alert>
      )}

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Filters
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel>County</InputLabel>
              <Select
                value={filters.county}
                label="County"
                onChange={handleFilterChange('county')}
              >
                <MenuItem value="">All Counties</MenuItem>
                <MenuItem value="Fulton">Fulton</MenuItem>
                <MenuItem value="DeKalb">DeKalb</MenuItem>
                <MenuItem value="Clayton">Clayton</MenuItem>
                <MenuItem value="Cobb">Cobb</MenuItem>
                <MenuItem value="Atlanta">Atlanta</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Min Investment Score"
              type="number"
              value={filters.min_score}
              onChange={handleFilterChange('min_score')}
              inputProps={{ min: 0, max: 100 }}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel>Status</InputLabel>
              <Select
                value={filters.status}
                label="Status"
                onChange={handleFilterChange('status')}
              >
                <MenuItem value="">All Statuses</MenuItem>
                <MenuItem value="discovered">Discovered</MenuItem>
                <MenuItem value="analyzing">Analyzing</MenuItem>
                <MenuItem value="analyzed">Analyzed</MenuItem>
                <MenuItem value="rejected">Rejected</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
        <Box mt={2} display="flex" gap={2}>
          <Button variant="contained" onClick={applyFilters}>
            Apply Filters
          </Button>
          <Button variant="outlined" onClick={clearFilters}>
            Clear Filters
          </Button>
        </Box>
      </Paper>

      {/* Properties Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Address</TableCell>
              <TableCell>City</TableCell>
              <TableCell>County</TableCell>
              <TableCell align="right">Price</TableCell>
              <TableCell align="right">Score</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Discovery Date</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {properties.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  <Typography variant="body2" color="text.secondary" py={3}>
                    No properties found. Start a discovery job to find properties.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              properties.map((property) => (
                <TableRow key={property.id} hover>
                  <TableCell>{property.address}</TableCell>
                  <TableCell>{property.city}</TableCell>
                  <TableCell>{property.county}</TableCell>
                  <TableCell align="right">
                    ${property.price?.toLocaleString() || 'N/A'}
                  </TableCell>
                  <TableCell align="right">
                    <Chip
                      label={property.investment_score || 'N/A'}
                      color={property.investment_score >= 80 ? 'success' : property.investment_score >= 60 ? 'warning' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={property.status || 'unknown'}
                      color={getStatusColor(property.status)}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {property.discovery_date ? new Date(property.discovery_date).toLocaleDateString() : 'N/A'}
                  </TableCell>
                  <TableCell align="center">
                    <Button size="small" variant="outlined">
                      View Details
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

export default Properties;
