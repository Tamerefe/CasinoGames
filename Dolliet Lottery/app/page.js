"use client";

import { useState, useEffect } from "react";

export default function Home() {
  const [userNumbers, setUserNumbers] = useState(Array(7).fill(""));
  const [lotteryNumbers, setLotteryNumbers] = useState(Array(7).fill("?"));
  const [countdown, setCountdown] = useState(9);
  const [resultMessage, setResultMessage] = useState("");
  const [showCountdown, setShowCountdown] = useState(false);

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
    return Array.from({ length: 7 }, () => Math.floor(Math.random() * 10));
  };

  const startLottery = () => {
    setShowCountdown(true);
    setCountdown(9);
    setResultMessage("");
    const newLotteryNumbers = generateLotteryNumbers();
    setTimeout(() => {
      setLotteryNumbers(newLotteryNumbers);
      checkResults(newLotteryNumbers);
    }, 11000);
    
    let timeleft = 9;
    const timer = setInterval(() => {
      timeleft--;
      setCountdown(timeleft);
      if (timeleft <= 0) clearInterval(timer);
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

  return (
    <div className="h-full w-full flex fixed items-center justify-center">
      <div className="bg-white p-4">
        <div className="bg-[rgb(0,255,13)] p-4">
          <div className="bg-[#ffff00] p-4">
            <div className="bg-zinc-900 p-12 text-white text-2xl">
              <h1 className="text-center m-3 mt-0">Dolliet Lottery</h1>
              {showCountdown && (
                <p className="text-center pb-2 mb-2">End to Change Your Mind {countdown}</p>
              )}
              <div className="flex justify-center gap-2">
                {lotteryNumbers.map((num, i) => (
                  <p key={i} className="h-11 w-11 bg-gray-100 rounded-full inline-block m-1 text-3xl font-righteous text-black text-center">{num}</p>
                ))}
              </div>
              <br />
              <button className="button1 p-2" onClick={startLottery}>Start Lottery</button>
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
