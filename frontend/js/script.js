document.addEventListener("DOMContentLoaded", () => {
  console.log("Portofolio loaded successfully.");

  //Smoooth Navigation

  const navLinks = document.querySelectorAll(".nav-links a");

  navLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      const targetId = link.getAttribute("href");

      if (!targetId || !targetId.startsWith("#")) {
        return;
      }

      const targetSection = document.querySelector(targetId);

      if (!targetSection) {
        return;
      }

      event.preventDefault();

      targetSection.scrollIntoView({
        behavior: "smooth",
      });
    });
  });

  // Contact form Submission
  const contactForm = document.querySelector("#contact-form");
  const formStatus = document.querySelector("#form-status");
  if (contactForm && formStatus) {
    contactForm.addEventListener("submit", async (event) => {
      event.preventDefault();

      const submitButton = contactForm.querySelector('button[type="submit"]');

      const nameInput = contactForm.querySelector("#name");
      const emailInput = contactForm.querySelector("#email");
      const messageInput = contactForm.querySelector("#message");

      console.log("Name input:", nameInput);
      console.log("Email input:", emailInput);
      console.log("Message input:", messageInput);

      //const formData = {
      //  name: contactForm.querySelector("#name").Value.trim(),
      //  email: contactForm.querySelector("#email").Value.trim(),
      //  message: contactForm.querySelector("#message").Value.trim(),
      //};

      const formData = {
        name: nameInput?.value?.trim(),
        email: emailInput?.value?.trim(),
        message: messageInput?.value?.trim(),
      };

      submitButton.disabled = true;
      formStatus.textContent = "Sending your message...";

      try {
        const response = await fetch(
          "https://sudarsan-portfolio-backend.onrender.com/api/contact/",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(formData),
          },
        );

        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.detail || "Unable to send your message.");
        }

        formStatus.textContent = result.message || "Message sent successfully!";

        contactForm.reset();
      } catch (error) {
        console.error("Contact form error:", error);

        formStatus.textContent =
          error.message || "Something went wrong. Please try again.";
      } finally {
        submitButton.disabled = false;
      }
    });
  }
});
