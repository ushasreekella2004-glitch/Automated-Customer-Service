import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Chip,
  InputLabel,
  MenuItem,
  FormControl,
  Select,
  CircularProgress,
  Alert,
  Pagination
} from '@mui/material';
import {
  Search as SearchIcon,
  ShoppingCart as CartIcon,
  Info as InfoIcon,
  Category as CategoryIcon
} from '@mui/icons-material';
import axios from 'axios';

const ProductSearch = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const categories = [
    'NVIDIA Electronics',
    'Apparel',
    'Lifestyle',
    'Drinkware',
    'Office',
    'Bags'
  ];

  useEffect(() => {
    loadProducts();
  }, [page, selectedCategory]);

  const loadProducts = async (query = '') => {
    setLoading(true);
    setError(null);

    try {
      const params = {
        limit: 12,
        page: page
      };

      if (query) {
        params.query = query;
      }
      if (selectedCategory) {
        params.category = selectedCategory;
      }

      const response = await axios.get('/api/products', { params });
      setProducts(response.data.products || []);
      setTotalPages(Math.ceil((response.data.total || 0) / 12));
    } catch (err) {
      setError('Failed to load products. Please try again.');
      console.error('Product search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    loadProducts(searchQuery);
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  const handleCategoryChange = (event) => {
    setSelectedCategory(event.target.value);
    setPage(1);
  };

  const handlePageChange = (event, value) => {
    setPage(value);
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const truncateDescription = (description, maxLength = 100) => {
    if (description.length <= maxLength) return description;
    return description.substring(0, maxLength) + '...';
  };

  return (
    <Box>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold' }}>
        Product Search
      </Typography>

      {/* Search Controls */}
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Search Products"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter product name or description..."
              disabled={loading}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={selectedCategory}
                onChange={handleCategoryChange}
                label="Category"
                disabled={loading}
              >
                <MenuItem value="">All Categories</MenuItem>
                {categories.map((category) => (
                  <MenuItem key={category} value={category}>
                    {category}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <Button
              fullWidth
              variant="contained"
              startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
              onClick={handleSearch}
              disabled={loading}
              sx={{ height: '56px' }}
            >
              {loading ? 'Searching...' : 'Search'}
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Products Grid */}
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress size={60} />
        </Box>
      ) : products.length > 0 ? (
        <>
          <Grid container spacing={3}>
            {products.map((product, index) => (
              <Grid item xs={12} sm={6} md={4} key={index}>
                <Card 
                  elevation={2} 
                  sx={{ 
                    height: '100%', 
                    display: 'flex', 
                    flexDirection: 'column',
                    transition: 'transform 0.2s',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 4
                    }
                  }}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                      <Typography variant="h6" sx={{ fontWeight: 'bold', flexGrow: 1 }}>
                        {product.name}
                      </Typography>
                      <Chip
                        label={formatPrice(product.price)}
                        color="primary"
                        size="small"
                      />
                    </Box>
                    
                    <Chip
                      icon={<CategoryIcon />}
                      label={product.category}
                      size="small"
                      variant="outlined"
                      sx={{ mb: 2 }}
                    />
                    
                    <Typography 
                      variant="body2" 
                      color="text.secondary" 
                      sx={{ mb: 2, minHeight: '60px' }}
                    >
                      {truncateDescription(product.description)}
                    </Typography>
                    
                    {product.subcategory && (
                      <Typography variant="caption" color="text.secondary">
                        Subcategory: {product.subcategory}
                      </Typography>
                    )}
                  </CardContent>
                  
                  <CardActions sx={{ p: 2, pt: 0 }}>
                    <Button
                      startIcon={<InfoIcon />}
                      variant="outlined"
                      size="small"
                      fullWidth
                    >
                      View Details
                    </Button>
                    <Button
                      startIcon={<CartIcon />}
                      variant="contained"
                      size="small"
                      fullWidth
                      sx={{ ml: 1 }}
                    >
                      Add to Cart
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>

          {/* Pagination */}
          {totalPages > 1 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={handlePageChange}
                color="primary"
                size="large"
              />
            </Box>
          )}
        </>
      ) : (
        <Paper elevation={1} sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
            No products found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Try adjusting your search criteria or browse by category.
          </Typography>
        </Paper>
      )}

      {/* Quick Actions */}
      <Paper elevation={1} sx={{ p: 3, mt: 3, bgcolor: 'grey.50' }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Quick Actions
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Button variant="outlined" size="small">
            View All Products
          </Button>
          <Button variant="outlined" size="small">
            Featured Products
          </Button>
          <Button variant="outlined" size="small">
            New Arrivals
          </Button>
          <Button variant="outlined" size="small">
            Best Sellers
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default ProductSearch;
