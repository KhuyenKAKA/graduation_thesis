<template>
  <div>
    <div class="footer-top-divider"></div>

    <footer class="footer">
      <div class="footer-container">
        <div class="footer-top-row">
          <div class="footer-logo">
            <img src="/assets/logo.png" alt="UniCompare" class="logo-image" />
            <span class="logo-text">UniCompare</span>
          </div>

          <div class="footer-main-links">
            <a href="#">About</a>
            <a href="#">Contact</a>
            <a href="#">Privacy</a>
            <a href="#">Users</a>
          </div>

          <div class="footer-social">
            <span>Follow us</span>
            <div class="social-icons">
              <a href="#" class="social-icon" title="Facebook">
                <img src="/assets/facebook-icon.png" alt="Facebook" />
              </a>
              <a href="#" class="social-icon" title="Twitter">
                <img src="/assets/twitter-icon.png" alt="Twitter/X" />
              </a>
              <a href="#" class="social-icon" title="LinkedIn">
                <img src="/assets/linkedin-icon.png" alt="LinkedIn" />
              </a>
              <a href="#" class="social-icon" title="Instagram">
                <img src="/assets/instagram-icon.png" alt="Instagram" />
              </a>
            </div>
          </div>
        </div>

        <div class="footer-grid-row">
          <div class="footer-col">
            <div class="footer-dropdown">
              <span>For Students</span>
              <span class="arrow">▼</span>
            </div>
            <div class="footer-dropdown">
              <span>For Professionals</span>
              <span class="arrow">▼</span>
            </div>
          </div>

          <div class="footer-col">
            <div class="footer-dropdown">
              <span>For institution</span>
              <span class="arrow">▼</span>
            </div>
          </div>

          <div class="footer-col">
            <div class="footer-legal-links">
              <a href="#">Cookies</a>
              <a href="#">Data Copyright</a>
              <a href="#">Terms & Conditions</a>
            </div>
          </div>

          <div class="footer-col newsletter-col">
            <label>Subscribe to our newsletter</label>
            <div class="newsletter-box">
              <input type="email" placeholder="Please enter your email" />
              <button class="btn-submit">
                <span>→</span>
              </button>
            </div>
          </div>
        </div>

        <div class="footer-copyright">
          <p>© UniCompare 1994 - 2026. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
</script>

<style scoped>
.footer-top-divider {
  width: 100%;
  height: 8px;
  background-color: #1f3ab0;
  margin: 0;
  padding: 0;
}

.footer {
  background: #ffffff;
  padding: 60px 50px 30px 50px;
  font-family: 'Inter', sans-serif;
}

.footer-container {
  max-width: 1300px;
  margin: 0 auto;
}

.footer-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 50px;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: bold;
  font-size: 24px;
  color: #1f3ab0;
}

.footer-logo .logo-image {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.footer-main-links {
  display: flex;
  gap: 40px;
}

.footer-main-links a {
  text-decoration: none;
  color: #333;
  font-size: 15px;
  transition: color 0.3s;
}

.footer-main-links a:hover {
  color: #1f3ab0;
}

.footer-social {
  display: flex;
  align-items: center;
  gap: 15px;
  font-size: 15px;
}

.social-icons {
  display: flex;
  gap: 10px;
}

.social-icon {
  width: 36px;
  height: 36px;
  background: #f5f5f5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  font-size: 14px;
  border: 1px solid #e0e0e0;
  transition: all 0.3s;
  overflow: hidden;
}

.social-icon:hover {
  background: #e0e0e0;
  transform: scale(1.1);
}

.social-icon img {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.footer-grid-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1.5fr;
  gap: 30px;
  padding-bottom: 40px;
}

.footer-dropdown {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  color: #333;
  font-size: 15px;
  cursor: pointer;
  width: 200px;
}

.footer-legal-links {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.footer-legal-links a {
  text-decoration: none;
  color: #333;
  font-size: 15px;
}

.newsletter-col label {
  display: block;
  font-weight: bold;
  margin-bottom: 15px;
  font-size: 15px;
}

.newsletter-box {
  display: flex;
  border: 1px solid #ddd;
  border-radius: 4px;
  max-width: 400px;
}

.newsletter-box input {
  flex: 1;
  padding: 12px;
  border: none;
  outline: none;
}

.btn-submit {
  background: #1f3ab0;
  color: white;
  border: none;
  padding: 0 20px;
  cursor: pointer;
  font-size: 20px;
}

.footer-copyright {
  border-top: 1px solid #eee;
  padding-top: 20px;
  text-align: center;
  color: #888;
  font-size: 13px;
}

@media (max-width: 768px) {
  .footer-top-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 20px;
  }

  .footer-grid-row {
    grid-template-columns: 1fr;
  }

  .footer-main-links {
    flex-direction: column;
    gap: 15px;
  }
}
</style>
