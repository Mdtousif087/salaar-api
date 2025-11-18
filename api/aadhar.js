const { google } = require('googleapis');

module.exports = async (req, res) => {
  const { aadhar } = req.query;

  if (!aadhar) {
    return res.status(400).json({ error: 'Aadhar parameter required' });
  }

  try {
    const auth = new google.auth.GoogleAuth({
      credentials: {
        client_email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
        private_key: process.env.GOOGLE_PRIVATE_KEY.replace(/\\n/g, '\n'),
      },
      scopes: ['https://www.googleapis.com/auth/drive.readonly'],
    });

    const drive = google.drive({ version: 'v3', auth });
    
    const response = await drive.files.get({
      fileId: process.env.GOOGLE_DRIVE_FILE_ID,
      alt: 'media',
    }, { responseType: 'text' });

    const database = JSON.parse(response.data);
    const result = database.find(item => item.id_number === aadhar);

    if (!result) {
      return res.status(404).json({ error: 'Aadhar not found' });
    }

    res.status(200).json(result);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Internal server error: ' + error.message });
  }
};
