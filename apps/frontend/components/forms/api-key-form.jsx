import React from 'react';

function ApiKeyForm() {
  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      // const response = await axios.post('/create-api-key');
      // const apiKey = response.data.api_key;
      const apiKey = 'sample-api-key'; // Remove this line when you uncomment the above lines

      // Copy the API key to the clipboard
      await navigator.clipboard.writeText(apiKey);

      alert('API key has been generated and copied to the clipboard');
    } catch (error) {
      alert('Failed to generate API key');
    }
  };

  return (
    <div className="max-w-md mx-auto bg-gray-900 text-white rounded-xl shadow-md overflow-hidden md:max-w-2xl m-3">
      <form onSubmit={handleSubmit} className="p-8">
        <button type="submit" className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-700">
          Generate and Copy API Key
        </button>
      </form>
    </div>
  );
}

export default ApiKeyForm;