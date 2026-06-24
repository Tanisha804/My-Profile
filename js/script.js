const typingRoles = [
  "Java Full Stack Developer",
  "Web Developer",
  "Backend Developer",
  "Freelancer"
];

const leadKey = "tanisha_portfolio_leads";

function saveLead(lead) {
  const leads = getAllLeads();
  leads.push({ ...lead, date: new Date().toISOString() });
  localStorage.setItem(leadKey, JSON.stringify(leads));
}

function getAllLeads() {
  try {
    return JSON.parse(localStorage.getItem(leadKey)) || [];
  } catch (error) {
    return [];
  }
}

function deleteLead(index) {
  const leads = getAllLeads();
  leads.splice(index, 1);
  localStorage.setItem(leadKey, JSON.stringify(leads));
}

window.saveLead = saveLead;
window.getAllLeads = getAllLeads;
window.deleteLead = deleteLead;

function initLoader() {
  const loader = document.querySelector(".loader");
  if (!loader) return;
  window.addEventListener("load", () => {
    setTimeout(() => loader.classList.add("is-hidden"), 450);
  });
}

function initNavigation() {
  const toggle = document.querySelector(".menu-toggle");
  const links = document.querySelector(".nav-links");
  if (!toggle || !links) return;
  toggle.addEventListener("click", () => links.classList.toggle("open"));
  links.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => links.classList.remove("open"));
  });
}

function initTyping() {
  const target = document.querySelector("[data-typing]");
  if (!target) return;
  let roleIndex = 0;
  let charIndex = 0;
  let deleting = false;

  function type() {
    const current = typingRoles[roleIndex];
    target.textContent = current.slice(0, charIndex);

    if (!deleting && charIndex < current.length) {
      charIndex += 1;
      setTimeout(type, 72);
      return;
    }

    if (!deleting && charIndex === current.length) {
      deleting = true;
      setTimeout(type, 1200);
      return;
    }

    if (deleting && charIndex > 0) {
      charIndex -= 1;
      setTimeout(type, 38);
      return;
    }

    deleting = false;
    roleIndex = (roleIndex + 1) % typingRoles.length;
    setTimeout(type, 280);
  }

  type();
}

function initReveal() {
  const items = document.querySelectorAll(".reveal");
  if (!items.length) return;
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.14 });
  items.forEach((item) => observer.observe(item));
}

function initCounters() {
  const counters = document.querySelectorAll("[data-count]");
  if (!counters.length) return;
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const target = Number(el.dataset.count);
      const suffix = el.dataset.suffix || "";
      let current = 0;
      const step = Math.max(1, Math.ceil(target / 52));
      const timer = setInterval(() => {
        current += step;
        if (current >= target) {
          current = target;
          clearInterval(timer);
        }
        el.textContent = `${current}${suffix}`;
      }, 28);
      observer.unobserve(el);
    });
  }, { threshold: 0.35 });
  counters.forEach((counter) => observer.observe(counter));
}

function initAccordion() {
  document.querySelectorAll(".accordion-button").forEach((button) => {
    button.addEventListener("click", () => {
      const item = button.closest(".accordion-item");
      if (!item) return;
      item.classList.toggle("open");
    });
  });
}

function initPortfolioFilters() {
  const buttons = document.querySelectorAll("[data-filter]");
  const cards = document.querySelectorAll("[data-category]");
  if (!buttons.length || !cards.length) return;
  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      buttons.forEach((btn) => btn.classList.remove("active"));
      button.classList.add("active");
      const filter = button.dataset.filter;
      cards.forEach((card) => {
        const show = filter === "all" || card.dataset.category === filter;
        card.style.display = show ? "grid" : "none";
      });
    });
  });
}

function setError(form, name, message) {
  const error = form.querySelector(`[data-error="${name}"]`);
  if (error) error.textContent = message;
}

function clearErrors(form) {
  form.querySelectorAll("[data-error]").forEach((error) => {
    error.textContent = "";
  });
}

function validateLeadForm(form, options = {}) {
  clearErrors(form);
  let valid = true;
  const data = new FormData(form);
  const name = String(data.get("name") || "").trim();
  const email = String(data.get("email") || "").trim();
  const mobile = String(data.get("mobile") || "").trim();
  const message = String(data.get("message") || "").trim();
  const terms = form.querySelector("[name='terms']");
  const file = form.querySelector("[name='file']");

  if (!name) {
    setError(form, "name", "Please enter your full name.");
    valid = false;
  } else if (!/^[A-Za-z ]+$/.test(name)) {
    setError(form, "name", "Name can contain letters and spaces only.");
    valid = false;
  }

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    setError(form, "email", "Please enter a valid email address.");
    valid = false;
  }

  if (!/^[6-9]\d{9}$/.test(mobile)) {
    setError(form, "mobile", "Please enter a valid 10 digit mobile number.");
    valid = false;
  }

  if (options.requireMessage && message.length < 12) {
    setError(form, "message", "Please share at least 12 characters about your project.");
    valid = false;
  }

  if (terms && !terms.checked) {
    setError(form, "terms", "Please accept the enquiry terms.");
    valid = false;
  }

  if (file && file.files.length) {
    const selected = file.files[0];
    const allowed = ["application/pdf", "image/png", "image/jpeg"];
    if (!allowed.includes(selected.type) || selected.size > 4 * 1024 * 1024) {
      setError(form, "file", "Upload a PDF, PNG, or JPG under 4 MB.");
      valid = false;
    }
  }

  return valid;
}

function initForms() {
  document.querySelectorAll("[data-lead-form]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const requireMessage = form.dataset.leadForm === "contact";
      if (!validateLeadForm(form, { requireMessage })) return;
      const data = new FormData(form);
      saveLead({
        name: data.get("name") || "",
        email: data.get("email") || "",
        mobile: data.get("mobile") || "",
        service: data.get("service") || data.get("businessType") || "General enquiry",
        message: data.get("message") || "Free consultation request"
      });
      form.reset();
      const success = form.querySelector(".success-message") || document.querySelector(`[data-success-for="${form.id}"]`);
      if (success) {
        success.classList.add("show");
        setTimeout(() => success.classList.remove("show"), 5200);
      }
      closeModal();
    });
  });

  document.querySelectorAll("[data-newsletter]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const data = new FormData(form);
      const name = String(data.get("name") || "").trim();
      const email = String(data.get("email") || "").trim();
      if (!name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return;
      saveLead({ name, email, mobile: "", service: "Newsletter", message: "Subscribed for website development tips" });
      form.reset();
      const success = form.querySelector(".success-message");
      if (success) success.classList.add("show");
    });
  });
}

function openModal() {
  const modal = document.querySelector(".modal");
  if (modal) modal.classList.add("show");
}

function closeModal() {
  const modal = document.querySelector(".modal");
  if (modal) modal.classList.remove("show");
}

function initModal() {
  document.querySelectorAll("[data-open-consultation]").forEach((button) => {
    button.addEventListener("click", openModal);
  });
  document.querySelectorAll("[data-close-modal]").forEach((button) => {
    button.addEventListener("click", closeModal);
  });
  const modal = document.querySelector(".modal");
  if (modal) {
    modal.addEventListener("click", (event) => {
      if (event.target === modal) closeModal();
    });
  }
}

function initFooterUtilities() {
  const time = document.querySelector("[data-live-time]");
  const visitors = document.querySelector("[data-visitors]");
  const top = document.querySelector(".back-top");

  if (time) {
    setInterval(() => {
      time.textContent = new Date().toLocaleString("en-IN", {
        dateStyle: "medium",
        timeStyle: "medium"
      });
    }, 1000);
  }

  if (visitors) {
    const count = Number(localStorage.getItem("tanisha_visitors") || "0") + 1;
    localStorage.setItem("tanisha_visitors", String(count));
    visitors.textContent = String(count).padStart(4, "0");
  }

  if (top) {
    window.addEventListener("scroll", () => {
      top.classList.toggle("show", window.scrollY > 600);
    });
    top.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  }
}

initLoader();
initNavigation();
initTyping();
initReveal();
initCounters();
initAccordion();
initPortfolioFilters();
initForms();
initModal();
initFooterUtilities();
