# 🌐 Báo Cáo Tương Tác Frontend với 8 Services Back-end

## 📋 Tổng Quan

Frontend của hệ thống Food Fast E-commerce cần tương tác với **8 microservices** thông qua **47 API endpoints** để cung cấp trải nghiệm người dùng hoàn chỉnh. Tất cả các requests đều đi qua **API Gateway** làm single entry point.

## 🎯 API Endpoints Tổng Quan

### 📊 Thống Kê Endpoints

- **Tổng số API Endpoints**: 47
- **Protected Endpoints**: 31 (66%)
- **Public Endpoints**: 16 (34%)
- **Services**: 9 nhóm API

### 📱 Endpoints theo từng Service

| Service | Endpoints | Mô tả |
|---------|-----------|-------|
| **API Gateway** | 3 | Health check, service discovery |
| **Authentication** | 7 | Login, register, OAuth, password reset |
| **User Management** | 7 | Profile, favorites, orders history |
| **Product Catalog** | 8 | Products, search, categories, reviews |
| **Order Management** | 5 | Create, track, cancel orders |
| **Shopping Cart** | 5 | Add, update, remove cart items |
| **Payment Processing** | 5 | Payment intent, confirm, methods |
| **Notifications** | 5 | User notifications, preferences |
| **Analytics** | 2 | Event tracking, dashboard |

## 🔄 Frontend Integration Patterns

### 1. 🔐 Authentication Flow

```javascript
// Authentication service example
class AuthService {
  async login(email, password) {
    const response = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    if (data.access_token) {
      localStorage.setItem('token', data.access_token);
      this.setupTokenRefresh(data.expires_in);
      return data;
    }
    throw new Error('Login failed');
  }
  
  getAuthHeaders() {
    const token = localStorage.getItem('token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }
}
```

**Flow Steps:**
1. User submits login form
2. Frontend calls `POST /auth/login`
3. Backend returns JWT token
4. Frontend stores token securely
5. Include token in Authorization header for protected requests
6. Handle token expiration and refresh

### 2. 🛍️ Product Browsing

```javascript
// Product service example
class ProductService {
  async getProducts(filters = {}) {
    const params = new URLSearchParams(filters);
    const response = await fetch(`/products?${params}`);
    return response.json();
  }
  
  async searchProducts(query, filters = {}) {
    const params = new URLSearchParams({ q: query, ...filters });
    const response = await fetch(`/products/search?${params}`);
    return response.json();
  }
  
  async getProductDetails(productId) {
    const response = await fetch(`/products/${productId}`);
    const product = await response.json();
    
    // Track product view
    analyticsService.trackEvent('product_view', { 
      product_id: productId,
      category: product.category 
    });
    
    return product;
  }
}
```

### 3. 🛒 Shopping Cart Management

```javascript
// Cart service example
class CartService {
  async addToCart(productId, quantity = 1, specialInstructions = '') {
    const response = await fetch('/cart/items', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authService.getAuthHeaders()
      },
      body: JSON.stringify({ 
        product_id: productId, 
        quantity,
        special_instructions: specialInstructions 
      })
    });
    
    if (response.ok) {
      analyticsService.trackEvent('add_to_cart', { 
        product_id: productId, 
        quantity 
      });
      this.updateCartBadge();
      this.showCartNotification('Product added to cart!');
    }
    
    return response.json();
  }
  
  async updateCartBadge() {
    const cart = await this.getCart();
    const badge = document.querySelector('.cart-badge');
    if (badge) {
      badge.textContent = cart.total_items;
      badge.style.display = cart.total_items > 0 ? 'block' : 'none';
    }
  }
}
```

### 4. 💳 Order & Payment Processing

```javascript
// Checkout service example
class CheckoutService {
  async processCheckout(orderData) {
    try {
      // Step 1: Create order
      const orderResponse = await fetch('/orders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authService.getAuthHeaders()
        },
        body: JSON.stringify(orderData)
      });
      
      const order = await orderResponse.json();
      
      // Step 2: Create payment intent
      const paymentResponse = await fetch('/payments/create-intent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authService.getAuthHeaders()
        },
        body: JSON.stringify({
          order_id: order.id,
          amount: order.total_amount,
          currency: 'usd',
          payment_method: 'stripe'
        })
      });
      
      const paymentIntent = await paymentResponse.json();
      
      // Step 3: Process payment with Stripe
      const stripe = Stripe(process.env.STRIPE_PUBLIC_KEY);
      const result = await stripe.confirmCardPayment(
        paymentIntent.client_secret,
        {
          payment_method: {
            card: cardElement,
            billing_details: {
              name: orderData.customer_name,
              email: orderData.customer_email
            }
          }
        }
      );
      
      if (result.error) {
        throw new Error(result.error.message);
      }
      
      // Step 4: Confirm payment
      await fetch('/payments/confirm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authService.getAuthHeaders()
        },
        body: JSON.stringify({
          payment_intent_id: paymentIntent.payment_intent_id
        })
      });
      
      // Step 5: Clear cart and redirect
      await cartService.clearCart();
      analyticsService.trackEvent('purchase', {
        order_id: order.id,
        amount: order.total_amount
      });
      
      return order;
      
    } catch (error) {
      console.error('Checkout failed:', error);
      throw error;
    }
  }
}
```

### 5. 🔔 Real-time Updates

```javascript
// Real-time service example
class RealTimeService {
  constructor() {
    this.socket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.connect();
  }
  
  connect() {
    this.socket = new WebSocket('ws://localhost:8000/ws');
    
    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };
    
    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };
    
    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      this.attemptReconnect();
    };
    
    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }
  
  handleMessage(data) {
    switch (data.type) {
      case 'order_status_update':
        this.updateOrderStatus(data.order_id, data.status);
        this.showNotification(`Order ${data.order_id}: ${data.status}`);
        break;
        
      case 'notification':
        this.showNotification(data.message);
        notificationService.addToInbox(data);
        break;
        
      case 'delivery_update':
        this.updateDeliveryTracking(data.order_id, data.location);
        break;
    }
  }
  
  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => this.connect(), 2000 * this.reconnectAttempts);
    }
  }
}
```

## 🛠️ Recommended Frontend Tech Stack

### Core Framework Options

#### React (Recommended)
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "axios": "^1.3.0",
    "@tanstack/react-query": "^4.24.0",
    "zustand": "^4.3.0",
    "@stripe/stripe-js": "^1.46.0",
    "socket.io-client": "^4.6.0",
    "@mui/material": "^5.11.0",
    "react-hook-form": "^7.43.0"
  }
}
```

#### Vue 3 (Alternative)
```json
{
  "dependencies": {
    "vue": "^3.2.0",
    "vue-router": "^4.1.0",
    "pinia": "^2.0.0",
    "axios": "^1.3.0",
    "vuetify": "^3.1.0",
    "@stripe/stripe-js": "^1.46.0",
    "socket.io-client": "^4.6.0"
  }
}
```

### Development Tools
```json
{
  "devDependencies": {
    "@vitejs/plugin-react": "^3.1.0",
    "vite": "^4.1.0",
    "typescript": "^4.9.0",
    "eslint": "^8.0.0",
    "prettier": "^2.8.0",
    "@testing-library/react": "^14.0.0",
    "vitest": "^0.28.0"
  }
}
```

## 📱 UI Components Architecture

### Component Structure
```
src/
├── components/
│   ├── common/           # Reusable components
│   │   ├── Button/
│   │   ├── Input/
│   │   ├── Loading/
│   │   └── Notification/
│   ├── layout/           # Layout components
│   │   ├── Header/
│   │   ├── Footer/
│   │   └── Sidebar/
│   └── features/         # Feature-specific components
│       ├── auth/
│       ├── products/
│       ├── cart/
│       ├── orders/
│       └── user/
├── pages/               # Page components
├── services/            # API services
├── hooks/              # Custom hooks
├── store/              # State management
├── utils/              # Utility functions
└── styles/             # Global styles
```

### Example Component Structure

```javascript
// src/components/features/products/ProductCard.jsx
import React from 'react';
import { useCart } from '../../../hooks/useCart';
import { useAnalytics } from '../../../hooks/useAnalytics';

const ProductCard = ({ product }) => {
  const { addToCart, isLoading } = useCart();
  const { trackEvent } = useAnalytics();
  
  const handleAddToCart = async () => {
    try {
      await addToCart(product.id, 1);
      trackEvent('add_to_cart', {
        product_id: product.id,
        product_name: product.name,
        price: product.price
      });
    } catch (error) {
      console.error('Failed to add to cart:', error);
    }
  };
  
  return (
    <div className="product-card">
      <img src={product.images[0]} alt={product.name} />
      <h3>{product.name}</h3>
      <p>${product.price}</p>
      <button 
        onClick={handleAddToCart}
        disabled={isLoading}
        className="add-to-cart-btn"
      >
        {isLoading ? 'Adding...' : 'Add to Cart'}
      </button>
    </div>
  );
};

export default ProductCard;
```

## 🔒 Security Best Practices

### 1. Token Management
```javascript
// Secure token storage
class TokenManager {
  static setToken(token) {
    // Use secure storage
    if (window.crypto && window.crypto.subtle) {
      // Store encrypted in production
      localStorage.setItem('token', token);
    }
  }
  
  static getToken() {
    return localStorage.getItem('token');
  }
  
  static removeToken() {
    localStorage.removeItem('token');
  }
  
  static isTokenExpired(token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return Date.now() >= payload.exp * 1000;
    } catch {
      return true;
    }
  }
}
```

### 2. Input Validation
```javascript
// Input validation utility
class Validator {
  static validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
  
  static validatePassword(password) {
    return password.length >= 8 && 
           /[A-Z]/.test(password) && 
           /[a-z]/.test(password) && 
           /\d/.test(password);
  }
  
  static sanitizeInput(input) {
    return input.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
  }
}
```

### 3. CSRF Protection
```javascript
// CSRF token handling
axios.interceptors.request.use((config) => {
  const token = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
  if (token) {
    config.headers['X-CSRF-TOKEN'] = token;
  }
  return config;
});
```

## 📈 Performance Optimization

### 1. Code Splitting
```javascript
// Lazy loading routes
import { lazy, Suspense } from 'react';

const Products = lazy(() => import('./pages/Products'));
const Orders = lazy(() => import('./pages/Orders'));
const Profile = lazy(() => import('./pages/Profile'));

function App() {
  return (
    <Router>
      <Suspense fallback={<Loading />}>
        <Routes>
          <Route path="/products" element={<Products />} />
          <Route path="/orders" element={<Orders />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </Suspense>
    </Router>
  );
}
```

### 2. API Response Caching
```javascript
// React Query for caching
import { useQuery } from '@tanstack/react-query';

const useProducts = (filters) => {
  return useQuery({
    queryKey: ['products', filters],
    queryFn: () => productService.getProducts(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });
};
```

### 3. Image Optimization
```javascript
// Lazy loading images
const LazyImage = ({ src, alt, ...props }) => {
  const [imageSrc, setImageSrc] = useState('');
  const [imageRef, setImageRef] = useState();
  
  useEffect(() => {
    let observer;
    
    if (imageRef && imageSrc !== src) {
      if (IntersectionObserver) {
        observer = new IntersectionObserver(
          entries => {
            entries.forEach(entry => {
              if (entry.isIntersecting) {
                setImageSrc(src);
                observer.unobserve(imageRef);
              }
            });
          },
          { threshold: 0.1 }
        );
        observer.observe(imageRef);
      } else {
        setImageSrc(src);
      }
    }
    
    return () => {
      if (observer && observer.unobserve) {
        observer.unobserve(imageRef);
      }
    };
  }, [src, imageSrc, imageRef]);
  
  return (
    <img
      {...props}
      ref={setImageRef}
      src={imageSrc}
      alt={alt}
    />
  );
};
```

## ✅ Frontend Integration Checklist

### 🔐 Authentication & Authorization
- [ ] Login/Register forms
- [ ] JWT token handling
- [ ] Token refresh mechanism
- [ ] OAuth integration (Google, Facebook)
- [ ] Password reset flow
- [ ] Logout functionality

### 👤 User Management
- [ ] User profile page
- [ ] Profile editing
- [ ] Avatar upload
- [ ] Account settings
- [ ] Order history
- [ ] Wishlist/Favorites

### 🛍️ Product Catalog
- [ ] Product listing with pagination
- [ ] Product search functionality
- [ ] Advanced filters
- [ ] Product detail pages
- [ ] Product reviews
- [ ] Category navigation

### 🛒 Shopping Experience
- [ ] Add to cart functionality
- [ ] Cart management
- [ ] Quantity updates
- [ ] Remove items
- [ ] Cart persistence
- [ ] Clear cart

### 📦 Order Management
- [ ] Checkout process
- [ ] Order confirmation
- [ ] Order tracking
- [ ] Order history
- [ ] Cancel orders
- [ ] Reorder functionality

### 💳 Payment Integration
- [ ] Payment form
- [ ] Stripe integration
- [ ] PayPal integration
- [ ] Saved payment methods
- [ ] Payment confirmation
- [ ] Receipt generation

### 🔔 Notifications
- [ ] Real-time notifications
- [ ] Notification center
- [ ] Email preferences
- [ ] Push notifications
- [ ] SMS notifications

### 📊 Analytics & Tracking
- [ ] Page view tracking
- [ ] Product view events
- [ ] Add to cart events
- [ ] Purchase events
- [ ] User behavior tracking

### 🌐 User Experience
- [ ] Responsive design
- [ ] Mobile optimization
- [ ] Loading states
- [ ] Error handling
- [ ] Offline support
- [ ] Accessibility (WCAG)
- [ ] Internationalization

### 🔧 Technical Requirements
- [ ] API error handling
- [ ] Network retry logic
- [ ] Caching strategy
- [ ] Code splitting
- [ ] Bundle optimization
- [ ] Testing coverage

## 🚀 Deployment & Development

### Development Environment
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm run test

# Build for production
npm run build
```

### Environment Variables
```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000
VITE_STRIPE_PUBLIC_KEY=pk_test_...
VITE_WEBSOCKET_URL=ws://localhost:8000/ws
VITE_ANALYTICS_TRACKING_ID=GA_TRACKING_ID

# .env.production
VITE_API_BASE_URL=https://api.foodfast.com
VITE_STRIPE_PUBLIC_KEY=pk_live_...
VITE_WEBSOCKET_URL=wss://api.foodfast.com/ws
VITE_ANALYTICS_TRACKING_ID=GA_TRACKING_ID
```

## 📖 Conclusion

Frontend của Food Fast E-commerce cần tương tác với 8 microservices thông qua 47 API endpoints để cung cấp trải nghiệm người dùng hoàn chỉnh. Với architecture được thiết kế tốt, frontend có thể:

- **Scalable**: Dễ dàng thêm features mới
- **Maintainable**: Code được tổ chức rõ ràng theo features
- **Performant**: Tối ưu loading và caching
- **Secure**: Bảo mật authentication và data
- **User-friendly**: UX/UI tối ưu cho nhiều devices

Việc implement theo đúng patterns và best practices sẽ đảm bảo hệ thống frontend hoạt động ổn định, hiệu quả và có thể mở rộng trong tương lai.
