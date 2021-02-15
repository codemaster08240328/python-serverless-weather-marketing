const path = require('path');

const templateList = [
  {
    name: 'forecast_email_template',
    subject: '{{subject}}'
  }
]

/**
 * @param {Object} serverless - Serverless instance
 * @param {Object} _options - runtime options
 * @returns {Promise<{name: string, subject: string, html: string, text}[]>}
 */

module.exports = async (serverless, _options) => {
  // You can load template configuration from filesystem using serverless object + runtime options
  // or from any other source like database or API

  const sesEmailTemplates = templateList.map((templateInfo) => {
    const { name, subject } = templateInfo;
    const templatePathHtml = path.join(__dirname, `./templates/${name}.html`);
    const templatePathTxt = path.join(__dirname, `./templates/${name}.txt`);

    console.log(serverless.utils.readFileSync(templatePathHtml));
    console.log(serverless.utils.readFileSync(templatePathTxt));
    return {
      name: name,
      subject: subject,
      html: serverless.utils.readFileSync(templatePathHtml),
      text: serverless.utils.readFileSync(templatePathTxt),
    };
  });

  return sesEmailTemplates;
};
