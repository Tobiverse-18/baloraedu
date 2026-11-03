import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

function PublicRoute() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="app-loading">
        <p>Loading Balora Edu...</p>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/schools" replace />;
  }

  return <Outlet />;
}

export default PublicRoute;