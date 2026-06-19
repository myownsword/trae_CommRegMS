<template>
  <div class="app">
    <header class="navbar">
      <div class="container navbar-inner">
        <router-link to="/" class="logo">
          <span class="logo-icon">🏘️</span>
          <span class="logo-text">社区活动报名管理系统</span>
        </router-link>
        <nav class="nav-links">
          <router-link to="/" class="nav-link" exact-active-class="active">
            活动列表
          </router-link>
          <router-link to="/activities/new" class="btn btn-primary btn-sm">
            + 发布活动
          </router-link>
        </nav>
      </div>
    </header>

    <main class="main-content">
      <div class="container">
        <router-view />
      </div>
    </main>

    <footer class="footer">
      <div class="container">
        <p>&copy; 2026 社区活动报名管理系统</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
</script>

<style scoped>
.navbar {
  background: white;
  border-bottom: 1px solid var(--gray-200);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 64px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--gray-900);
  text-decoration: none;
}

.logo-icon {
  font-size: 1.5rem;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-link {
  color: var(--gray-600);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.5rem 0;
}

.nav-link:hover,
.nav-link.active {
  color: var(--primary);
}

.main-content {
  padding: 2rem 0;
  min-height: calc(100vh - 64px - 80px);
}

.footer {
  background: white;
  border-top: 1px solid var(--gray-200);
  padding: 1.5rem 0;
  text-align: center;
  color: var(--gray-500);
  font-size: 0.8125rem;
}

@media (max-width: 640px) {
  .logo-text {
    display: none;
  }

  .navbar-inner {
    height: 56px;
  }

  .main-content {
    padding: 1rem 0;
  }
}
</style>
