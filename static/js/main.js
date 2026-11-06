document.querySelectorAll('.flash').forEach((el) => {
  setTimeout(() => { el.classList.add('hide'); setTimeout(() => el.remove(), 400); }, 6500);
});
