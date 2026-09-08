// OTAI SECTION: header

let currentGrid = '';

// OTAI SECTION: functions

function initEffortTask() {
  currentGrid = document.querySelector('#grid').textContent;
  document.querySelector('#submit-answer').addEventListener('click', submitAnswer);
  document.querySelector('#answer-input').addEventListener('keypress', function(e) {
      if (e.key === 'Enter') submitAnswer();
  });
  document.querySelector('#answer-input').addEventListener('keydown', function(e) {
      if (['.', 'e', 'E', '+', '-'].includes(e.key)) e.preventDefault();
  });
}

function liveRecv(data) {
  if (data.type === 'next_trial') {
      currentGrid = data.grid;
      document.querySelector('#grid').textContent = data.grid;
      const fb = document.querySelector('#feedback');
      if (data.last_correct) {
          fb.textContent = 'Correct!';
      } else {
          fb.textContent = 'Incorrect.';
      }
      document.querySelector('#answer-input').disabled = false;
      document.querySelector('#submit-answer').disabled = false;
      document.querySelector('#answer-input').focus();
  } else if (data.type === 'done') {
      document.querySelector('#feedback').textContent = 'All grids completed!';
      document.querySelector('#answer-input').disabled = true;
      document.querySelector('#submit-answer').disabled = true;
      document.querySelector('#submit-answer').closest('form').requestSubmit();
  } else if (data.type === 'timeout') {
      document.querySelector('#feedback').textContent = 'Time is up!';
  }
}

function submitAnswer() {
  const input = document.querySelector('#answer-input');
  const answer = input.value;
  if (answer === '') return;
  liveSend({answer: answer, grid: currentGrid});
  input.value = '';
  input.disabled = true;
  docQuerySelectorStrict('#submit-answer').disabled = true;
}

// OTAI SECTION: footer

initEffortTask();