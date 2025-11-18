const { google } = require('googleapis');

module.exports = async (req, res) => {
  const { number } = req.query;

  if (!number) {
    return res.status(400).json({ error: 'Number parameter required' });
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
    
    // ✅ CORRECTED: File content as text le rahe hain
    const response = await drive.files.get({
      fileId: process.env.GOOGLE_DRIVE_FILE_ID,
      alt: 'media',
    }, { responseType: 'text' });

    // ✅ JSON parse karna padega
    const database = JSON.parse(response.data);
    const result = database.find(item => item.mobile === number);

    if (!result) {
      return res.status(404).json({ error: 'Number not found' });
    }

    res.status(200).json(result);
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Internal server error: ' + error.message });
  }
};
