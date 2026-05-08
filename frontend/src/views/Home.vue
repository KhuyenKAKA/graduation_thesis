<template>
  <div class="home">
    <!-- Header Component -->
    <Header />

    <!-- Recommendation Section -->
    <section class="recommendation-section">
      <div class="recommendation-container">
        <div class="recommendation-label">Course Recommendation</div>
        <h1 class="recommendation-title">Connect with your dream university today</h1>

        <div class="recommendation-points">
          <div class="point">
            <span class="checkmark">✓</span>
            <span>Get personalised admission support for the top universities</span>
          </div>
          <div class="point">
            <span class="checkmark">✓</span>
            <span>Get academic details from universities in just a few clicks.</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Rankings Cards -->
    <section class="rankings-section">
      <div class="rankings-container">
        <div class="ranking-card">
          <div class="card-image">
            <img src="/assets/world.jpg" alt="World Ranking" />
          </div>
          <div class="card-content">
            <h3>UC World University Rankings 2026</h3>
            <p>Discover the top-performing universities around the world</p>
            <button class="btn-explore" @click="goToRanking()">
              Explore <span>→</span>
            </button>
          </div>
        </div>

        <div class="ranking-card">
          <div class="card-image">
            <img src="/assets/europe.jpg" alt="By Subject" />
          </div>
          <div class="card-content">
            <h3>UC World University Rankings: Europe 2026</h3>
            <p>Discover the top universities in Europe with the UC Europe University Rankings.</p>
            <button class="btn-explore" @click="goToRanking(2)">
              Explore <span>→</span>
            </button>
          </div>
        </div>

        <div class="ranking-card">
          <div class="card-image">
            <img src="/assets/asia.jpg" alt="Asia Ranking" />
          </div>
          <div class="card-content">
            <h3>UC World University Rankings: Asia 2026</h3>
            <p>Discover the top universities in Asia with the UC Asia University Rankings.</p>
            <button class="btn-explore" @click="goToRanking(1)">
              Explore <span>→</span>
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Testimonials Section -->
    <section class="testimonials-section">
      <div class="testimonials-container">
        <h2 class="testimonials-title">What students say</h2>
        <p class="testimonials-subtitle">Hear how we've supported students like you to find their perfect study destination</p>

        <div class="testimonials-grid">
          <div class="testimonial-card">
            <div class="testimonial-text">
              <p class="quote-text">"My counsellor's assistance at every step has been invaluable, and I cannot thank him enough for making my dreams a reality."</p>
            </div>
            <div class="testimonial-author">
              <img src="/assets/student1.avif" alt="Pranay Kasat" class="author-image" />
              <div>
                <p class="author-name">Pranay Kasat</p>
                <p class="author-info">Master of Science in Global Logistics, WP. Carey School of Business, Arizona State University</p>
              </div>
            </div>
          </div>

          <div class="testimonial-center-card">
            <img src="/assets/student2.avif" alt="Student" class="center-image" />
            <p class="center-name">Pranay Kasat</p>
            <p class="center-info">Master of Science in Global Logistics, W.P. Carey School of Business, Arizona State University</p>
          </div>

          <div class="testimonial-card">
            <div class="testimonial-text">
              <p class="quote-text">"UniCompare were a huge help from the very beginning. When I felt overwhelmed, it was my counsellor who helped me clarify my goals and find a programme best suited for my future."</p>
            </div>
            <div class="testimonial-author">
              <img src="/assets/student3.webp" alt="Bilal Jose" class="author-image" />
              <div>
                <p class="author-name">Bilal Jose</p>
                <p class="author-info">BCh in Mechanical Engineering, Arizona State University</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Partners Section -->
    <section class="partners-section">
      <div class="partners-container">
        <h2>Over 650 global partner universities</h2>

        <div class="partners-grid">
          <div v-for="logo in currentPartnerLogos" :key="logo" class="partner-logo">
            <img :src="`/assets/${logo}`" :alt="logo" />
          </div>
        </div>

        <div class="pagination">
          <span
            v-for="(_, index) in partnerPages"
            :key="index"
            class="dot"
            :class="{ active: currentPage === index }"
            @click="currentPage = index"
          ></span>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <Footer />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'

const router = useRouter()

const goToRanking = (region_id = null) => {
  if (region_id) {
    router.push({ path: '/universities', query: { region_id } })
  } else {
    router.push({ path: '/universities' })
  }
}

// Partner logos organized by pages
const allPartnerLogos = [
  // Page 1
  'Harvard-University-Logo.png',
  'Boston-University-Logo.png',
  'American_university.png',
  'Columbia-University-Logo.png',
  'Duke-University-Logo.png',
  'Cornell-University-Logo.png',
  'Northwestern-University-Logo.png',
  'Chicago-University-Logo.png',
  // Page 2
  'Georgetown-University-Logo.png',
  'National-University-of-Singapore-Logo.png',
  'Melbourne-University-Logo.png',
  'Auckland-University-Logo.png',
  'Otago-University-Logo.png',
  'Moscow-State-University-Logo.png',
  'Northeastern-University-Logo.png',
  'Brown-Unversity-Logo.png',
  // Page 3
  'Oregon-State-University-Logo-1.png',
  'Cairo-University-Logo.png',
  'Harvard-University-Logo.png',
  'Columbia-University-Logo.png',
  'Duke-University-Logo.png',
  'Chicago-University-Logo.png',
  'Boston-University-Logo.png',
  'Cornell-University-Logo.png'
]

const currentPage = ref(0)
const logosPerPage = 8

// Create pages
const partnerPages = computed(() => {
  const pages = []
  for (let i = 0; i < allPartnerLogos.length; i += logosPerPage) {
    pages.push(allPartnerLogos.slice(i, i + logosPerPage))
  }
  return pages
})

// Get current page logos
const currentPartnerLogos = computed(() => {
  return partnerPages.value[currentPage.value] || []
})
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.home {
  width: 100%;
}

/* Recommendation Section */
.recommendation-section {
  background: linear-gradient(to right, #e8f0ff, #f5f0ff);
  padding: 60px 50px 32px;
  margin-bottom: 0;
}

.recommendation-container {
  max-width: 1400px;
  margin: 0 auto;
}

.recommendation-label {
  color: #666;
  font-size: 13px;
  margin-bottom: 16px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.recommendation-title {
  font-size: 32px;
  color: #000;
  margin-bottom: 24px;
}

.recommendation-points {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.point {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #333;
}

.checkmark {
  color: #22c55e;
  font-weight: bold;
  font-size: 18px;
}

/* Rankings Section */
.rankings-section {
  padding: 32px 50px 60px;
  background: white;
}

.rankings-container {
  max-width: 1400px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 32px;
}

.ranking-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
}

.ranking-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.card-image {
  position: relative;
  width: 100%;
  height: 180px;
  background: linear-gradient(135deg, #ffa500, #ffb84d);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.ranking-badge {
  position: absolute;
  top: 0;
  left: 0;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  padding: 8px 12px;
  font-size: 11px;
  font-weight: bold;
  width: 100%;
}

.card-content {
  padding: 24px;
}

.card-content h3 {
  font-size: 16px;
  margin-bottom: 12px;
  color: #000;
}

.card-content p {
  font-size: 13px;
  color: #666;
  margin-bottom: 24px;
  line-height: 1.6;
}

.btn-explore {
  background: #1f3ab0;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 600;
  font-size: 13px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-explore:hover {
  background: #1a2d8a;
  transform: translateX(4px);
}

/* Testimonials Section */
.testimonials-section {
  background: #e8f0ff;
  padding: 80px 50px;
}

.testimonials-container {
  max-width: 1400px;
  margin: 0 auto;
}

.testimonials-title {
  text-align: center;
  font-size: 36px;
  margin-bottom: 16px;
  color: #000;
}

.testimonials-subtitle {
  text-align: center;
  font-size: 16px;
  color: #666;
  margin-bottom: 60px;
}

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 32px;
  align-items: center;
}

.testimonial-card {
  background: #4a7bdb;
  color: white;
  padding: 32px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
}

.quote-text {
  font-size: 14px;
  line-height: 1.8;
  margin-bottom: 32px;
  font-style: italic;
}

.testimonial-author {
  display: flex;
  align-items: center;
  gap: 12px;
}

.author-image {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.author-name {
  font-weight: 600;
  font-size: 14px;
  margin: 0;
}

.author-info {
  font-size: 12px;
  opacity: 0.9;
  margin: 4px 0 0 0;
}

.testimonial-center-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.center-image {
  width: 150px;
  height: 200px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 16px;
}

.center-name {
  font-weight: 600;
  color: #000;
  margin-bottom: 8px;
}

.center-info {
  font-size: 12px;
  color: #666;
  text-align: center;
}

/* Partners Section */
.partners-section {
  padding: 80px 50px;
  background: white;
}

.partners-container {
  max-width: 1400px;
  margin: 0 auto;
}

.partners-container h2 {
  text-align: center;
  font-size: 32px;
  margin-bottom: 60px;
  color: #000;
}

.partners-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 40px;
}

.partner-logo {
  background: white;
  padding: 24px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 120px;
  border: 1px solid #e0e0e0;
  transition: transform 0.3s;
}

.partner-logo:hover {
  transform: translateY(-4px);
}

.partner-logo img {
  max-width: 100%;
  max-height: 80px;
  object-fit: contain;
}

.pagination {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #cbd5e1;
  cursor: pointer;
  transition: background 0.3s;
}

.dot.active {
  background: #1f3ab0;
}

/* Responsive cho điện thoại */
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
