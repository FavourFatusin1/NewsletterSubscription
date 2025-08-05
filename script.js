document.getElementById('subscribe-form').addEventListener('submit', async function(e) {
  e.preventDefault();

  const email = document.getElementById('email').value.trim();
  const message = document.getElementById('message');

  // Basic email validation
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailPattern.test(email)) {
    message.textContent = "Invalid email address!";
    message.style.color = "red";
    return;
  }

  try {
    const response = await fetch("https://tdwqh53l6i.execute-api.us-east-1.amazonaws.com/prod/subscribe", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email })
    });

    if (response.ok) {
      message.textContent = "Subscription successful!";
      message.style.color = "green";
      alert(`Subscription sent to ${email}`);  // <-- popup alert here
      document.getElementById('email').value = "";
    } else {
      const errorData = await response.json();
      message.textContent = `Error: ${errorData.error || 'Subscription failed'}`;
      message.style.color = "red";
    }
  } catch (err) {
    message.textContent = "Request failed. Try again.";
    message.style.color = "red";
    console.error(err);
  }
});
