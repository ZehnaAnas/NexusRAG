import { useEffect, useRef, useState } from "react";
import Sidebar from "./components/Sidebar.jsx";
import ChatPanel from "./components/ChatPanel.jsx";
import { uploadFile, getStatus, askQuestion } from "./api.js";

export default function App() {
  const [files, setFiles] = useState([]); // [{ name, status }]
  const [activeFileName, setActiveFileName] = useState(null);
  const [chats, setChats] = useState({}); // { [fileName]: [{role, content}] }
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const pollTimers = useRef({});

  const activeFile = files.find((f) => f.name === activeFileName) || null;
  const activeMessages = activeFileName ? chats[activeFileName] || [] : [];

  useEffect(() => {
    return () => {
      Object.values(pollTimers.current).forEach(clearInterval);
    };
  }, []);

  const pollStatus = (fileName) => {
    if (pollTimers.current[fileName]) return;
    pollTimers.current[fileName] = setInterval(async () => {
      try {
        const { status } = await getStatus(fileName);
        setFiles((prev) =>
          prev.map((f) => (f.name === fileName ? { ...f, status } : f))
        );
        if (status === "completed" || status?.startsWith("Failed")) {
          clearInterval(pollTimers.current[fileName]);
          delete pollTimers.current[fileName];
        }
      } catch {
        clearInterval(pollTimers.current[fileName]);
        delete pollTimers.current[fileName];
      }
    }, 2000);
  };

  const handleFileSelected = async (file) => {
    setUploading(true);
    try {
      const { message: fileName, status } = await uploadFile(file);
      setFiles((prev) => [
        { name: fileName, status },
        ...prev.filter((f) => f.name !== fileName),
      ]);
      setActiveFileName(fileName);
      setChats((prev) => ({ ...prev, [fileName]: prev[fileName] || [] }));
      pollStatus(fileName);
    } catch (err) {
      alert(err.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleAsk = async (question) => {
    if (!activeFileName) return;
    const fileName = activeFileName;
    setChats((prev) => ({
      ...prev,
      [fileName]: [...(prev[fileName] || []), { role: "user", content: question }],
    }));
    setAsking(true);
    try {
      const answer = await askQuestion(question, fileName);
      setChats((prev) => ({
        ...prev,
        [fileName]: [...(prev[fileName] || []), { role: "assistant", content: answer }],
      }));
    } catch (err) {
      setChats((prev) => ({
        ...prev,
        [fileName]: [
          ...(prev[fileName] || []),
          {
            role: "assistant",
            content: `Sorry, something went wrong: ${err.message}`,
          },
        ],
      }));
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="flex h-screen w-full overflow-hidden">
      <Sidebar
        files={files}
        activeFile={activeFileName}
        onSelectFile={setActiveFileName}
        uploading={uploading}
      />
      <ChatPanel
        activeFile={activeFile}
        messages={activeMessages}
        onAsk={handleAsk}
        asking={asking}
        onUploadFile={handleFileSelected}
        uploading={uploading}
      />
    </div>
  );
}
