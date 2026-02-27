document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;

        // Create participants section
        const participantsSection = document.createElement("div");
        participantsSection.className = "participants-section";

        if (details.participants.length > 0) {
          const title = document.createElement("strong");
          title.textContent = `Participants (${details.participants.length}):`;
          participantsSection.appendChild(title);

          const ul = document.createElement("ul");
          details.participants.forEach((participant) => {
            const li = document.createElement("li");
            li.className = "participant-item";

            const email = document.createElement("span");
            email.textContent = participant;

            const deleteBtn = document.createElement("button");
            deleteBtn.className = "delete-btn";
            deleteBtn.innerHTML = "✕";
            deleteBtn.type = "button";
            deleteBtn.title = "Remove participant";

            deleteBtn.addEventListener("click", async (e) => {
              e.preventDefault();
              try {
                const response = await fetch(
                  `/activities/${encodeURIComponent(name)}/unregister?email=${encodeURIComponent(participant)}`,
                  { method: "POST" }
                );

                if (response.ok) {
                  fetchActivities(); // Refresh the list
                } else {
                  const error = await response.json();
                  alert("Error: " + (error.detail || "Failed to remove participant"));
                }
              } catch (error) {
                alert("Error removing participant");
                console.error("Error:", error);
              }
            });

            li.appendChild(email);
            li.appendChild(deleteBtn);
            ul.appendChild(li);
          });
          participantsSection.appendChild(ul);
        } else {
          const em = document.createElement("em");
          em.textContent = "No participants yet";
          participantsSection.appendChild(em);
        }

        activityCard.appendChild(participantsSection);
        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities(); // Refresh the activity list to show the new participant
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
