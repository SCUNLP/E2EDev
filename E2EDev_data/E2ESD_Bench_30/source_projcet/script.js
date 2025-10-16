const badgeForm = document.querySelector('[data-testid="badgeForm"]');
const downloadBadge = document.querySelector('[data-testid="dwnBadge"]');

badgeForm.addEventListener('submit', function (event) {
  event.preventDefault();

  const formcontainer = document.querySelector('[data-testid="formContainer"]');
  formcontainer.style.display = 'none';
  const eventname = document.querySelector('[data-testid="eventname"]').value;
  const name = document.querySelector('[data-testid="name"]').value;
  const designation = document.querySelector('[data-testid="designation"]').value;
  const company = "@" + document.querySelector('[data-testid="company"]').value;
  const access = document.querySelector('[data-testid="access"]').value;

  const id = 'ID' + Math.floor(Math.random() * 10000).toString().padStart(4, '0');

  document.querySelector('[data-testid="badgeEvent"]').textContent = eventname;
  document.querySelector('[data-testid="badgeName"]').textContent = name;
  document.querySelector('[data-testid="badgeDesignation"]').textContent = designation;
  document.querySelector('[data-testid="badgecontainer"]').textContent = company;
  document.querySelector('[data-testid="badgeAccess"]').textContent = access;

  const qrcodeElement = document.querySelector('[data-testid="qrcode"]');
  qrcodeElement.innerHTML = '';

  $(qrcodeElement).qrcode({
    text: `ID: ${id}\Event: ${eventname}\nName: ${name}\nDesignation: ${designation}\nCompany: ${company}\nAccess: ${access}`,
    width: 128,
    height: 128
  });

  document.querySelector('[data-testid="badge"]').style.display = 'block';
  downloadBadge.style.display = 'block';
});

downloadBadge.addEventListener('click', function (e) {
  e.preventDefault();
  const badgeElement = document.querySelector('[data-testid="badge"]');
  htmlToImage.toPng(badgeElement)
    .then(function (dataUrl) {
      const link = document.createElement('a');
      link.download = 'badge.png';
      link.href = dataUrl;
      link.click();
    })
    .catch(function (error) {
      console.error('Error converting HTML to image:', error);
    });
});
