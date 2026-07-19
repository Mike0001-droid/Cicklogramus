<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1 class="auth-title">
          <span>Циклограммус</span>
        </h1>
        <p class="auth-subtitle">Система планирования проектов</p>
      </div>

      <!-- Вкладки -->
      <ul class="nav nav-tabs auth-tabs">
        <li class="nav-item">
          <a
            class="nav-link"
            :class="{ active: isLogin }"
            @click="isLogin = true"
            href="#"
            @click.prevent
          >
            Вход
          </a>
        </li>
        <li class="nav-item">
          <a
            class="nav-link"
            :class="{ active: !isLogin }"
            @click="isLogin = false"
            href="#"
            @click.prevent
          >
            Регистрация
          </a>
        </li>
      </ul>

      <!-- Форма входа -->
      <form v-if="isLogin" @submit.prevent="handleLogin" class="auth-form">
        <div class="mb-3">
          <label for="login-username" class="form-label">Имя пользователя</label>
          <input
            id="login-username"
            v-model="loginData.username"
            type="text"
            class="form-control"
            placeholder="Введите имя пользователя"
            required
          />
        </div>

        <div class="mb-3">
          <label for="login-password" class="form-label">Пароль</label>
          <input
            id="login-password"
            v-model="loginData.password"
            type="password"
            class="form-control"
            placeholder="Введите пароль"
            required
          />
        </div>

        <div v-if="loginError" class="alert alert-danger">
          {{ loginError }}
        </div>

        <button type="submit" class="btn btn-primary w-100" :disabled="isLoading">
          <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
          {{ isLoading ? 'Вход...' : 'Войти' }}
        </button>
      </form>

      <!-- Форма регистрации -->
      <form v-else @submit.prevent="handleRegister" class="auth-form">
        <div class="mb-3">
          <label for="reg-username" class="form-label">Имя пользователя</label>
          <input
            id="reg-username"
            v-model="registerData.username"
            type="text"
            class="form-control"
            placeholder="Придумайте имя пользователя"
            required
            minlength="3"
          />
        </div>

        <div class="mb-3">
          <label for="reg-email" class="form-label">Email (необязательно)</label>
          <input
            id="reg-email"
            v-model="registerData.email"
            type="email"
            class="form-control"
            placeholder="example@mail.com"
          />
        </div>

        <div class="mb-3">
          <label for="reg-password" class="form-label">Пароль</label>
          <input
            id="reg-password"
            v-model="registerData.password"
            type="password"
            class="form-control"
            placeholder="Минимум 6 символов"
            required
            minlength="6"
          />
        </div>

        <div class="mb-3">
          <label for="reg-password-confirm" class="form-label">Подтвердите пароль</label>
          <input
            id="reg-password-confirm"
            v-model="registerData.password_confirm"
            type="password"
            class="form-control"
            placeholder="Повторите пароль"
            required
          />
        </div>

        <div v-if="registerError" class="alert alert-danger">
          {{ registerError }}
        </div>

        <button type="submit" class="btn btn-success w-100" :disabled="isLoading">
          <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
          {{ isLoading ? 'Регистрация...' : 'Зарегистрироваться' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import { authService, setAuthToken } from '../services/api';

export default {
  name: 'Auth',
  data() {
    return {
      isLogin: true,
      isLoading: false,
      loginData: {
        username: '',
        password: ''
      },
      registerData: {
        username: '',
        email: '',
        password: '',
        password_confirm: ''
      },
      loginError: '',
      registerError: ''
    }
  },
  methods: {
    async handleLogin() {
      this.isLoading = true;
      this.loginError = '';

      try {
        const response = await authService.login(
          this.loginData.username,
          this.loginData.password
        );

        const { access, refresh, user } = response;

        // Сохраняем токены
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
        localStorage.setItem('user', JSON.stringify(user));

        // Настраиваем axios
        setAuthToken(access);

        // Уведомляем родительский компонент
        this.$emit('authSuccess', user);

      } catch (error) {
        console.error('Login error:', error);
        if (error.response?.data?.detail) {
          this.loginError = error.response.data.detail;
        } else if (error.response?.data?.password) {
          this.loginError = error.response.data.password[0];
        } else {
          this.loginError = 'Ошибка входа. Проверьте имя пользователя и пароль.';
        }
      } finally {
        this.isLoading = false;
      }
    },

    async handleRegister() {
      // Валидация паролей
      if (this.registerData.password !== this.registerData.password_confirm) {
        this.registerError = 'Пароли не совпадают';
        return;
      }

      this.isLoading = true;
      this.registerError = '';

      try {
        const response = await authService.register(this.registerData);

        const { access, refresh, user } = response;

        // Сохраняем токены
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
        localStorage.setItem('user', JSON.stringify(user));

        // Настраиваем axios
        setAuthToken(access);

        // Уведомляем родительский компонент
        this.$emit('authSuccess', user);

      } catch (error) {
        console.error('Register error:', error);
        if (error.response?.data) {
          const errors = error.response.data;
          if (errors.username) {
            this.registerError = errors.username[0];
          } else if (errors.password) {
            this.registerError = errors.password[0];
          } else if (errors.detail) {
            this.registerError = errors.detail;
          }
        } else {
          this.registerError = 'Ошибка регистрации. Попробуйте позже.';
        }
      } finally {
        this.isLoading = false;
      }
    }
  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.auth-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  padding: 40px;
  width: 100%;
  max-width: 420px;
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-title {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.logo {
  font-size: 32px;
}

.auth-subtitle {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.auth-tabs {
  margin-bottom: 30px;
  border-bottom: 2px solid #e9ecef;
}

.auth-tabs .nav-link {
  border: none;
  color: #666;
  font-weight: 500;
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.auth-tabs .nav-link:hover {
  color: #667eea;
}

.auth-tabs .nav-link.active {
  color: #667eea;
}

.auth-tabs .nav-link.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: #667eea;
}

.auth-form .form-label {
  font-weight: 600;
  color: #555;
  margin-bottom: 6px;
}

.auth-form .form-control {
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.3s ease;
}

.auth-form .form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.btn {
  padding: 12px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.btn-success {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
  border: none;
}

.btn-success:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(17, 153, 142, 0.4);
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
