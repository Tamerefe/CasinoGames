"use client";

import { useState, useEffect } from "react";

export default function Home() {
  const [mounted, setMounted] = useState(false);
  const [userNumbers, setUserNumbers] = useState(Array(7).fill(""));
  const [lotteryNumbers, setLotteryNumbers] = useState(Array(7).fill("?"));
  const [revealedBalls, setRevealedBalls] = useState(Array(7).fill(false));
  const [countdown, setCountdown] = useState(9);
  const [resultMessage, setResultMessage] = useState("");
  const [showCountdown, setShowCountdown] = useState(false);
  const [isRevealing, setIsRevealing] = useState(false);
  const [showWarning, setShowWarning] = useState(true);

  // Ensure client-side rendering
  useEffect(() => {
    setMounted(true);
  }, []);

  // Legal warning component
  const LegalWarning = () => (
    <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50">
      <div className="bg-white p-8 rounded-lg max-w-2xl mx-4 text-center">
        <h1 className="text-3xl font-bold text-red-600 mb-6">⚠️ WARNING: EDUCATIONAL SOFTWARE ONLY ⚠️</h1>
        <div className="text-lg space-y-2 mb-6">
          <p className="text-red-600 font-semibold">• NO REAL MONEY INVOLVED</p>
          <p className="text-red-600 font-semibold">• NOT REAL GAMBLING</p>
          <p className="text-red-600 font-semibold">• FOR EDUCATIONAL PURPOSES ONLY</p>
          <p className="text-red-600 font-semibold">• AGE 18+ ONLY</p>
        </div>
        <div className="text-gray-700 mb-6">
          <p>This game demonstrates programming concepts and game mechanics.</p>
          <p>All monetary values are fictional and for educational purposes only.</p>
        </div>
        <button 
          onClick={() => setShowWarning(false)}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
        >
          I Understand - Continue to Game
        </button>
      </div>
    </div>
  );

  const handleInputChange = (index, value) => {
    if (/^\d*$/.test(value)) { // Only allow numeric values
      const newNumbers = [...userNumbers];
      newNumbers[index] = value;
      setUserNumbers(newNumbers);
    }
  };

  const getColor = (value) => {
    switch (value) {
      case "1": return "red";
      case "2": return "blue";
      case "3": return "green";
      case "4": return "yellow";
      case "5": return "purple";
      case "6": return "orange";
      case "7": return "pink";
      case "8": return "brown";
      case "9": return "gray";
      case "0": return "black";
      default: return "black";
    }
  };

  const generateLotteryNumbers = () => {
    // Only generate random numbers on client side
    if (typeof window === 'undefined') return Array(7).fill(0);
    return Array.from({ length: 7 }, () => Math.floor(Math.random() * 10));
  };

  const revealBall = (index, finalNumbers) => {
    return new Promise((resolve) => {
      setTimeout(() => {
        setLotteryNumbers(prev => {
          const newNumbers = [...prev];
          newNumbers[index] = finalNumbers[index];
          return newNumbers;
        });
        setRevealedBalls(prev => {
          const newRevealed = [...prev];
          newRevealed[index] = true;
          return newRevealed;
        });
        resolve();
      }, index * 800); // Her top 800ms arayla açılır
    });
  };

  const startLottery = () => {
    setShowCountdown(true);
    setCountdown(9);
    setResultMessage("");
    setRevealedBalls(Array(7).fill(false));
    setIsRevealing(false);
    
    const newLotteryNumbers = generateLotteryNumbers();
    
    let timeleft = 9;
    const timer = setInterval(() => {
      timeleft--;
      setCountdown(timeleft);
      if (timeleft <= 0) {
        clearInterval(timer);
        // Countdown bittikten sonra animasyonlu açılma başlar
        setTimeout(() => {
          animateBallReveal(newLotteryNumbers);
        }, 1000);
      }
    }, 1000);
  };

  const animateBallReveal = async (finalNumbers) => {
    setIsRevealing(true);
    
    // Topları tek tek aç
    for (let i = 0; i < 7; i++) {
      await revealBall(i, finalNumbers);
    }
    
    // Tüm toplar açıldıktan sonra sonucu kontrol et
    setTimeout(() => {
      checkResults(finalNumbers);
      setIsRevealing(false);
    }, 1000);
  };

  const checkResults = (newLotteryNumbers) => {
    const matches = userNumbers.filter((num, i) => num == newLotteryNumbers[i]).length;
    let message = "";
    switch (matches) {
      case 1: message = "Congratulations! You won an amortized prize!"; break;
      case 2: message = "Congratulations! You won $500!"; break;
      case 3: message = "Congratulations! You won $5,000!"; break;
      case 4: message = "Congratulations! You won $10,000!"; break;
      case 5: message = "Congratulations! You won $200,000!"; break;
      case 6: message = "Congratulations! You won $500,000!"; break;
      case 7: message = "Congratulations! You won $1,000,000!"; break;
      default: message = "You didn't win this time. Try again!";
    }
    setResultMessage(message);
  };

  // Don't render until client-side
  if (!mounted) {
    return (
      <div className="h-full w-full flex fixed items-center justify-center">
        <div className="bg-white p-4">
          <div className="bg-[rgb(0,255,13)] p-4">
            <div className="bg-[#ffff00] p-4">
              <div className="bg-zinc-900 p-12 text-white text-2xl">
                <h1 className="text-center m-3 mt-0">Dolliet Lottery</h1>
                <p className="text-center">Loading...</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show legal warning first
  if (showWarning) {
    return <LegalWarning />;
  }

  return (
    <div className="h-full w-full flex fixed items-center justify-center">
      <div className="bg-white p-4">
        <div className="bg-[rgb(0,255,13)] p-4">
          <div className="bg-[#ffff00] p-4">
            <div className="bg-zinc-900 p-12 text-white text-2xl">
              <h1 className="text-center m-3 mt-0">Dolliet Lottery</h1>
              <p className="text-center text-yellow-300 text-sm mb-2">Educational Simulation Only - No Real Money Involved</p>
              {showCountdown && (
                <p className="text-center pb-2 mb-2">End to Change Your Mind {countdown}</p>
              )}
              {isRevealing && (
                <p className="text-center pb-2 mb-2 text-yellow-400 animate-pulse">
                  🎲 Revealing Numbers... 🎲
                </p>
              )}
              <div className="flex justify-center gap-2">
                {lotteryNumbers.map((num, i) => (
                  <div
                    key={i}
                    className={`h-11 w-11 rounded-full inline-block m-1 text-3xl font-righteous text-black text-center flex items-center justify-center transition-all duration-500 ${
                      revealedBalls[i] 
                        ? 'bg-yellow-300 scale-110 shadow-lg animate-bounce' 
                        : 'bg-gray-100 hover:bg-gray-200'
                    }`}
                    style={{
                      transform: revealedBalls[i] ? 'scale(1.1) rotate(360deg)' : 'scale(1)',
                      boxShadow: revealedBalls[i] ? '0 0 20px rgba(255, 255, 0, 0.8)' : 'none'
                    }}
                  >
                    {num}
                  </div>
                ))}
              </div>
              <br />
              <button 
                className="button1 p-2 disabled:opacity-50 disabled:cursor-not-allowed" 
                onClick={startLottery}
                disabled={isRevealing}
              >
                {isRevealing ? "Revealing..." : "Start Lottery"}
              </button>
              <h3 className="text-center mt-3 mb-3 pb-3 pt-3">Choose Your Lucky Numbers</h3>
              <div className="flex justify-center gap-2">
                {userNumbers.map((num, i) => (
                  <input
                    key={i}
                    type="text"
                    maxLength="1"
                    autoComplete="off"
                    value={num}
                    onChange={(e) => handleInputChange(i, e.target.value)}
                    className="text-center border p-2 ml-2 w-10"
                    style={{ color: getColor(num) }}
                    disabled={isRevealing}
                  />
                ))}
              </div>
              <br />
              <p className="text-center text-xs">{resultMessage}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
