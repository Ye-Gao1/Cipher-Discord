import React, { useEffect, useState } from 'react';
import {
  ChakraProvider,
  Box,
  Heading,
  Text,
  Stack,
  Container,
  Button,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from '@chakra-ui/react';
import axios from 'axios';
import yaml from 'yaml';
import Login from './Login';

function App() {
  const [userData, setUserData] = useState({});
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userId, setUserId] = useState('');

  useEffect(() => {
    if (isLoggedIn) {
      fetchData();
    }
  }, [isLoggedIn]);

  const fetchData = () => {
    axios.get('./encrypted_messages.yaml')
      .then((response) => {
        const parsedData = yaml.parse(response.data);
        setUserData(parsedData);
      })
      .catch((error) => {
        console.error('Error fetching YAML file:', error);
      });
  };

  const handleLogin = (loginUserId) => {
    setIsLoggedIn(true);
    setUserId(loginUserId);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUserId('');
    setUserData({});
  };

  const handleRefresh = () => {
    fetchData();
  };

  const getUserMessages = (data) => {
    if (Array.isArray(data)) {
      return data;
    }
    return data?.messages || [];
  };

  const getUserKeys = (data) => {
    if (Array.isArray(data)) {
      return {};
    }
    return data?.keys || {};
  };

  return (
    <ChakraProvider>
      <Container maxW="container.lg" p={4}>
        <Heading as="h1" size="xl" mb={4}>
          Cipher Dashboard
        </Heading>
        {!isLoggedIn ? (
          <Login onLogin={handleLogin} />
        ) : (
          <>
            <Button onClick={handleLogout} mr={2} mb={4}>Logout</Button>
            <Button onClick={handleRefresh} mb={4}>Refresh Data</Button>
            {userData[userId] ? (
              <Tabs>
                <TabList>
                  <Tab>Encrypted Messages</Tab>
                  <Tab>Saved Keys</Tab>
                </TabList>
                <TabPanels>
                  <TabPanel>
                    <Stack spacing={4}>
                      <Heading as="h2" size="md" mb={2}>
                        User ID: {userId}
                      </Heading>
                      {getUserMessages(userData[userId]).map((message, index) => (
                        <Box key={index} p={2} borderWidth="1px" borderRadius="md">
                          <Text><strong>Original:</strong> {message.message}</Text>
                          <Text><strong>Encrypted:</strong> {message.encrypted}</Text>
                          <Text><strong>Key:</strong> {message.key}</Text>
                        </Box>
                      ))}
                    </Stack>
                  </TabPanel>
                  <TabPanel>
                    <Stack spacing={4}>
                      <Heading as="h2" size="md" mb={2}>
                        Saved Keys
                      </Heading>
                      {Object.entries(getUserKeys(userData[userId])).map(([name, key], index) => (
                        <Box key={index} p={2} borderWidth="1px" borderRadius="md">
                          <Text><strong>Name:</strong> {name}</Text>
                          <Text><strong>Key:</strong> {key}</Text>
                        </Box>
                      ))}
                    </Stack>
                  </TabPanel>
                </TabPanels>
              </Tabs>
            ) : (
              <Text>No data found for this user.</Text>
            )}
          </>
        )}
      </Container>
    </ChakraProvider>
  );
}

export default App;