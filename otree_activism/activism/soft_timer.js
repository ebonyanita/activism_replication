// OTAI SECTION: header

var softTimerInterval = null;


// OTAI SECTION: functions

function startSoftTimer() {
  var container = docQuerySelectorStrict('[data-soft-timer]');
  var timeLeft = parseInt(container.getAttribute('data-soft-timer'));
  var intervalMs = parseInt(container.getAttribute('data-interval-ms'));
  var display = eleQuerySelectorStrict(container, '.soft-timer-time');
  var countdownSpan = eleQuerySelectorStrict(container, '.soft-timer-countdown');
  var messageSpan = eleQuerySelectorStrict(container, '.soft-timer-message');
  container.style.display = 'block';
  display.textContent = timeLeft;
  softTimerInterval = setInterval(function () {
      timeLeft--;
      display.textContent = timeLeft;
      if (timeLeft <= 0) {
          clearInterval(softTimerInterval);
          softTimerInterval = null;
          countdownSpan.style.display = 'none';
          messageSpan.style.display = 'inline';
      }
  }, intervalMs);
  
}

// OTAI SECTION: footer

startSoftTimer();
