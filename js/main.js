(function () {
  'use strict';

  const IMG = 'assets/images/';

  function asset(path) {
    return IMG + path;
  }

  /** 仅使用本地静态资源，网站运行不依赖外网 */
  function localImage(base, kind) {
    return [asset(`${base}.jpg`), asset(`${base}.svg`)];
  }

  function createPlaceholderDataUri(title, kind) {
    const accent = kind === 'military' ? '#00e8ff' : '#ffd54f';
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 375">
      <rect width="600" height="375" fill="#120818"/>
      <circle cx="300" cy="170" r="80" fill="${accent}" opacity="0.15"/>
      <text x="300" y="200" text-anchor="middle" fill="${accent}" font-family="system-ui,sans-serif" font-size="20">${title}</text>
    </svg>`;
    return `data:image/svg+xml,${encodeURIComponent(svg)}`;
  }

  const lampProducts = [
    {
      name: '节日彩灯',
      desc: '春节、元宵、国庆等节庆主题彩灯，支持龙年彩灯、新年花灯定制。',
      tag: 'FESTIVAL',
      images: localImage('lamp-festival', 'lamp')
    },
    {
      name: '公园景观灯',
      desc: '城市公园、商业广场氛围彩灯与景观灯饰，打造夜游亮化场景。',
      tag: 'PARK',
      images: localImage('lamp-park', 'lamp')
    },
    {
      name: '民俗花灯',
      desc: '传承中原民俗花灯技艺，兔子彩灯、特色花灯、氛围彩灯多样呈现。',
      tag: 'FOLK',
      images: localImage('lamp-folk', 'lamp')
    },
    {
      name: '大型花灯灯组',
      desc: '大型花灯、龙形彩灯、主题灯组，适用于灯展与景区核心展示位。',
      tag: 'LARGE',
      images: localImage('lamp-dragon', 'lamp')
    },
    {
      name: '装饰花灯',
      desc: '道具花灯、装饰彩灯、花灯灯笼，商业街区与文旅街区氛围营造。',
      tag: 'DECOR',
      images: localImage('lamp-decor', 'lamp')
    },
    {
      name: '彩灯定制设计',
      desc: '彩灯设计、灯具定制、灯光定制全案服务，支持来图来样定制。',
      tag: 'CUSTOM',
      images: localImage('lamp-custom', 'lamp')
    },
    {
      name: '景观花灯',
      desc: '景观花灯、节庆用品组合方案，适配景区常态化夜游运营需求。',
      tag: 'LANDSCAPE',
      images: localImage('lamp-landscape', 'lamp')
    },
    {
      name: '国庆节主题彩灯',
      desc: '国庆主题氛围彩灯、红旗元素灯组，市政庆典与商业活动首选。',
      tag: 'NATIONAL',
      images: localImage('lamp-national', 'lamp')
    }
  ];

  const militaryProducts = [
    {
      name: '歼-20 战斗机模型',
      desc: '高仿真歼-20战斗机展示模型，适用于国防教育展、航空主题展与影视拍摄道具。',
      tag: 'AIR FORCE',
      images: localImage('military-j20', 'military')
    },
    {
      name: '主战坦克模型',
      desc: '99A、96式等主战坦克仿真模型，支持静态展示与动态可驾驶定制。',
      tag: 'TANK',
      images: localImage('military-tank', 'military')
    },
    {
      name: '航母军舰模型',
      desc: '航空母舰、军舰模型定制，军事博物馆与主题公园核心展陈装备。',
      tag: 'NAVY',
      images: localImage('military-carrier', 'military')
    },
    {
      name: '装甲战车模型',
      desc: '步兵战车、轮式装甲车等高逼真模型，研学基地与拓展营地标配。',
      tag: 'ARMOR',
      images: localImage('military-armor', 'military')
    },
    {
      name: '导弹发射车模型',
      desc: '东风系列导弹车模型，动静两种车型，军事展览高辨识度展品。',
      tag: 'MISSILE',
      images: localImage('military-missile', 'military')
    },
    {
      name: '武装直升机模型',
      desc: '武直-10等武装直升机模型，航空国防教育展陈系列产品。',
      tag: 'HELI',
      images: localImage('military-heli', 'military')
    },
    {
      name: '国防教育基地套装',
      desc: '坦克、战机、火炮组合展陈方案，一站式研学基地装备配置服务。',
      tag: 'EDU',
      images: localImage('military-edu', 'military')
    },
    {
      name: '影视军事道具',
      desc: '影视美术道具置景，高还原军事装备模型，满足剧组拍摄精度要求。',
      tag: 'FILM',
      images: localImage('military-film', 'military')
    }
  ];

  const HERO_IMAGES = localImage('hero-dragon', 'lamp');
  const ABOUT_IMAGES = localImage('about-festival', 'lamp');

  function bindImage(img, sources, alt, kind) {
    img.alt = alt;
    img.loading = img.loading || 'lazy';

    const list = [...sources, createPlaceholderDataUri(alt, kind)];
    let index = 0;

    const markLoaded = () => {
      img.classList.add('loaded');
      const shimmer = img.parentElement?.querySelector('.img-shimmer');
      if (shimmer) shimmer.remove();
    };

    const tryNext = () => {
      if (index >= list.length) {
        img.classList.add('img-fallback');
        return;
      }
      img.src = list[index];
      index += 1;
    };

    img.addEventListener('load', markLoaded);
    img.onerror = tryNext;
    tryNext();

    if (img.complete && img.naturalWidth > 0) {
      markLoaded();
    }
  }

  function createProductCard(product, index, type) {
    const card = document.createElement('article');
    card.className = 'product-card reveal tilt-card';
    card.dataset.tilt = '';
    card.style.transitionDelay = `${index * 0.08}s`;

    const imgWrap = document.createElement('div');
    imgWrap.className = 'product-card-img';

    const tag = document.createElement('span');
    tag.className = 'product-tag';
    tag.textContent = product.tag;

    const shimmer = document.createElement('div');
    shimmer.className = 'img-shimmer';
    shimmer.setAttribute('aria-hidden', 'true');

    const img = document.createElement('img');
    img.width = 600;
    img.height = 375;
    bindImage(img, product.images, product.name, type);

    const body = document.createElement('div');
    body.className = 'product-card-body';
    body.innerHTML = `<h3>${product.name}</h3><p>${product.desc}</p>`;

    const glow = document.createElement('div');
    glow.className = 'card-glow';
    glow.setAttribute('aria-hidden', 'true');

    imgWrap.append(tag, shimmer, img);
    card.append(glow, imgWrap, body);

    if (type === 'military') {
      card.classList.add('product-card--military');
    }

    return card;
  }

  function renderProducts() {
    const lampGrid = document.getElementById('lamp-grid');
    const militaryGrid = document.getElementById('military-grid');

    lampProducts.forEach((product, i) => {
      lampGrid.appendChild(createProductCard(product, i, 'lamp'));
    });

    militaryProducts.forEach((product, i) => {
      militaryGrid.appendChild(createProductCard(product, i, 'military'));
    });
  }

  function initHeroAndAboutImages() {
    const heroImg = document.getElementById('hero-img');
    const aboutImg = document.getElementById('about-img');

    if (heroImg) {
      heroImg.loading = 'eager';
      bindImage(heroImg, HERO_IMAGES, '龙形彩灯花灯灯展', 'lamp');
    }

    if (aboutImg) {
      bindImage(aboutImg, ABOUT_IMAGES, '节日彩灯花灯展示', 'lamp');
    }
  }

  function initNav() {
    const header = document.getElementById('header');
    const navToggle = document.getElementById('nav-toggle');
    const nav = document.getElementById('nav');

    window.addEventListener('scroll', () => {
      header.classList.toggle('scrolled', window.scrollY > 40);
    }, { passive: true });

    navToggle.addEventListener('click', () => {
      const isOpen = nav.classList.toggle('open');
      navToggle.classList.toggle('active', isOpen);
      navToggle.setAttribute('aria-expanded', isOpen);
    });

    nav.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => {
        nav.classList.remove('open');
        navToggle.classList.remove('active');
        navToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  function initCounters() {
    const counters = document.querySelectorAll('.stat-num[data-count]');

    const animateCounter = (el) => {
      const target = parseInt(el.dataset.count, 10);
      const duration = 1500;
      const start = performance.now();

      const tick = (now) => {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.floor(eased * target);
        if (progress < 1) requestAnimationFrame(tick);
        else el.textContent = target;
      };

      requestAnimationFrame(tick);
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.5 });

    counters.forEach((c) => observer.observe(c));
  }

  function initReveal() {
    const reveals = document.querySelectorAll(
      '.reveal, .section-header, .service-card, .process-step, .about-grid > *'
    );

    reveals.forEach((el) => el.classList.add('reveal'));

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

    reveals.forEach((el) => observer.observe(el));
  }

  function initParticles() {
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) return;

    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const ctx = canvas.getContext('2d');
    let particles = [];
    let animationId;
    let mouseX = 0;
    let mouseY = 0;

    const colors = [
      { r: 0, g: 229, b: 255 },
      { r: 255, g: 77, b: 77 },
      { r: 255, g: 200, b: 55 }
    ];

    function resize() {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }

    function createParticles() {
      const count = Math.min(100, Math.floor(window.innerWidth / 16));
      particles = Array.from({ length: count }, () => {
        const c = colors[Math.floor(Math.random() * colors.length)];
        return {
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.45,
          vy: (Math.random() - 0.5) * 0.45,
          size: Math.random() * 2.2 + 0.6,
          alpha: Math.random() * 0.55 + 0.25,
          color: c
        };
      });
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach((p, i) => {
        const dx = mouseX - p.x;
        const dy = mouseY - p.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 180 && dist > 0) {
          p.vx += (dx / dist) * 0.02;
          p.vy += (dy / dist) * 0.02;
        }

        p.x += p.vx;
        p.y += p.vy;
        p.vx *= 0.99;
        p.vy *= 0.99;

        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.color.r},${p.color.g},${p.color.b},${p.alpha})`;
        ctx.fill();

        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const ddx = p.x - p2.x;
          const ddy = p.y - p2.y;
          const d = Math.sqrt(ddx * ddx + ddy * ddy);

          if (d < 130) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            const a = 0.1 * (1 - d / 130);
            ctx.strokeStyle = `rgba(${p.color.r},${p.color.g},${p.color.b},${a})`;
            ctx.stroke();
          }
        }
      });

      animationId = requestAnimationFrame(draw);
    }

    resize();
    createParticles();
    if (!reduced) draw();

    window.addEventListener('resize', () => {
      resize();
      createParticles();
    });

    window.addEventListener('mousemove', (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    }, { passive: true });
  }

  function initCursorGlow() {
    const glow = document.getElementById('cursor-glow');
    if (!glow || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    let x = 0;
    let y = 0;
    let cx = 0;
    let cy = 0;

    window.addEventListener('mousemove', (e) => {
      x = e.clientX;
      y = e.clientY;
    }, { passive: true });

    const animate = () => {
      cx += (x - cx) * 0.12;
      cy += (y - cy) * 0.12;
      glow.style.transform = `translate(${cx - 200}px, ${cy - 200}px)`;
      requestAnimationFrame(animate);
    };

    animate();
  }

  function initTiltCards() {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    document.querySelectorAll('.tilt-card').forEach((card) => {
      card.addEventListener('mousemove', (e) => {
        const rect = card.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width - 0.5;
        const y = (e.clientY - rect.top) / rect.height - 0.5;
        const mx = ((e.clientX - rect.left) / rect.width) * 100;
        const my = ((e.clientY - rect.top) / rect.height) * 100;
        card.style.setProperty('--mx', `${mx}%`);
        card.style.setProperty('--my', `${my}%`);
        card.style.transform = `perspective(900px) rotateY(${x * 10}deg) rotateX(${-y * 10}deg) translateY(-8px)`;
      });

      card.addEventListener('mouseleave', () => {
        card.style.transform = '';
      });
    });
  }

  function initMagneticButtons() {
    document.querySelectorAll('.btn-magnetic').forEach((btn) => {
      btn.addEventListener('mousemove', (e) => {
        const rect = btn.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        btn.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px)`;
      });

      btn.addEventListener('mouseleave', () => {
        btn.style.transform = '';
      });
    });
  }

  function initHeroParallax() {
    const hero = document.querySelector('.hero-content');
    const heroBg = document.querySelector('.hero-bg img');
    if (!hero || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      if (y < window.innerHeight) {
        hero.style.transform = `translateY(${y * 0.25}px)`;
        if (heroBg) heroBg.style.transform = `scale(1.08) translateY(${y * 0.35}px)`;
      }
    }, { passive: true });
  }

  function initLanternFloat() {
    const container = document.getElementById('lantern-float');
    if (!container || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    for (let i = 0; i < 12; i++) {
      const el = document.createElement('span');
      el.className = 'floating-lantern';
      el.style.left = `${Math.random() * 100}%`;
      el.style.animationDelay = `${Math.random() * 8}s`;
      el.style.animationDuration = `${10 + Math.random() * 12}s`;
      el.style.width = `${8 + Math.random() * 14}px`;
      el.style.height = `${10 + Math.random() * 16}px`;
      container.appendChild(el);
    }
  }

  function initSparkleButtons() {
    document.querySelectorAll('.btn-primary').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

        const rect = btn.getBoundingClientRect();
        for (let i = 0; i < 10; i++) {
          const angle = Math.random() * Math.PI * 2;
          const dist = 30 + Math.random() * 35;
          const spark = document.createElement('span');
          spark.className = 'btn-spark';
          spark.style.left = `${e.clientX - rect.left}px`;
          spark.style.top = `${e.clientY - rect.top}px`;
          spark.style.setProperty('--tx', `${Math.cos(angle) * dist}px`);
          spark.style.setProperty('--ty', `${Math.sin(angle) * dist}px`);
          btn.appendChild(spark);
          setTimeout(() => spark.remove(), 700);
        }
      });
    });
  }

  function initForm() {
    const form = document.getElementById('contact-form');
    if (!form) return;

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      const originalText = btn.textContent;
      btn.textContent = '提交成功！';
      btn.disabled = true;

      setTimeout(() => {
        btn.textContent = originalText;
        btn.disabled = false;
        form.reset();
      }, 2500);
    });
  }

  renderProducts();
  initHeroAndAboutImages();
  initNav();
  initCounters();
  initReveal();
  initParticles();
  initCursorGlow();
  initTiltCards();
  initMagneticButtons();
  initHeroParallax();
  initLanternFloat();
  initSparkleButtons();
  initForm();
})();
