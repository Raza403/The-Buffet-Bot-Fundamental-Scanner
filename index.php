<?php
// ERROR REPORTING (Turn off for production, on for debug)
ini_set('display_errors', 1);
error_reporting(E_ALL);

// DB CONFIG
$host = 'localhost'; $db = 'investor_dashboard'; $user = 'root'; $pass = 'root'; $port = 8889; 
$conn = new mysqli($host, $user, $pass, $db, $port);

if ($conn->connect_error) { die("Connection failed: " . $conn->connect_error); }

// 1. SURVIVORS: Sorted by Quality (ROIC)
$sql_survivors = "SELECT * FROM stocks WHERE status = 'SURVIVOR' ORDER BY roic_current DESC";
$res_survivors = $conn->query($sql_survivors);
$survivor_count = $res_survivors ? $res_survivors->num_rows : 0;

// 2. REJECTED: Sorted Alphabetically
$sql_rejected = "SELECT * FROM stocks WHERE status = 'REJECTED' ORDER BY ticker ASC";
$res_rejected = $conn->query($sql_rejected);

// 3. STATS
$total_scanned = $conn->query("SELECT COUNT(*) as c FROM stocks")->fetch_assoc()['c'];
$rejected_count = $total_scanned - $survivor_count;

// HELPER: Get Color for Valuation
function getValuationColor($status) {
    if ($status === 'BARGAIN') return 'text-emerald-400 border-emerald-500/50 bg-emerald-900/20';
    if ($status === 'FAIR') return 'text-amber-400 border-amber-500/50 bg-amber-900/20';
    return 'text-rose-400 border-rose-500/50 bg-rose-900/20';
}
?>

<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code & Capital | Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { mono: ['JetBrains Mono', 'monospace'] },
                    colors: { 
                        bg: '#0A0C10', 
                        panel: '#12161D', 
                        accent: '#00D185', 
                        danger: '#FF2E63', 
                        mute: '#586776' 
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-bg text-gray-300 font-mono p-4 md:p-10 min-h-screen">

    <header class="flex flex-col xl:flex-row justify-between items-start xl:items-end border-b border-gray-800 pb-8 mb-10 gap-6">
        <div>
            <div class="flex items-center gap-3 mb-2">
                <div class="w-3 h-3 bg-accent rounded-full animate-pulse"></div>
                <h1 class="text-3xl md:text-4xl font-black tracking-tighter text-white uppercase">
                    Code & Capital <span class="text-gray-700">|</span> <span class="text-accent">WARREN BUFFETT MODEL</span>
                </h1>
            </div>
            <p class="text-mute text-sm md:text-base font-medium tracking-wide">
                "MARKETS ARE RANDOM; <span class="text-white">CASH FLOW IS FACT.</span>"
            </p>
        </div>
        
        <div class="flex gap-10 bg-panel px-6 py-3 rounded-lg border border-gray-800">
            <div class="text-right">
                <span class="block text-[10px] text-mute font-bold uppercase tracking-wider">Universe Scanned</span>
                <span class="text-2xl font-bold text-white"><?php echo $total_scanned; ?></span>
            </div>
            <div class="text-right border-l border-gray-700 pl-8">
                <span class="block text-[10px] text-mute font-bold uppercase tracking-wider">Rejected</span>
                <span class="text-2xl font-bold text-danger"><?php echo $rejected_count; ?></span>
            </div>
            <div class="text-right border-l border-gray-700 pl-8">
                <span class="block text-[10px] text-mute font-bold uppercase tracking-wider">Elite Survivors</span>
                <span class="text-3xl font-bold text-accent drop-shadow-[0_0_8px_rgba(0,209,133,0.4)]"><?php echo $survivor_count; ?></span>
            </div>
        </div>
    </header>

    <div class="mb-16">
        <div class="flex items-center gap-4 mb-6">
            <h2 class="text-accent text-sm font-bold uppercase tracking-[0.2em] border-l-4 border-accent pl-4">
                Valid Assets (Survivors)
            </h2>
            <div class="h-px bg-gray-800 flex-grow"></div>
        </div>
        
        <?php if($survivor_count > 0): ?>
            <div class="grid grid-cols-1 md:grid-cols-3 2xl:grid-cols-3 gap-8">
                <?php while($row = $res_survivors->fetch_assoc()): 
                    $valColor = getValuationColor($row['valuation_status']);
                ?>
                    <div class="bg-panel border border-gray-800 p-6 rounded-xl hover:border-accent/50 transition-all duration-300 shadow-2xl relative group">
                        
                        <div class="flex justify-between items-start mb-6">
                            <div>
                                <h3 class="text-4xl font-black text-white tracking-tighter"><?php echo $row['ticker']; ?></h3>
                                <p class="text-xs text-mute font-bold uppercase mt-1"><?php echo $row['company_name']; ?></p>
                            </div>
                            <div class="text-right flex flex-col items-end">
                                <span class="text-xl font-bold text-gray-200 block">$<?php echo number_format($row['price'], 2); ?></span>
                                <span class="text-[10px] font-bold px-2 py-1 rounded border mt-2 <?php echo $valColor; ?>">
                                    <?php echo $row['valuation_status']; ?>
                                </span>
                            </div>
                        </div>

                        <div class="grid grid-cols-2 gap-4 mb-6">
                            <div class="bg-[#0f1218] p-3 rounded border border-gray-800/50">
                                <span class="block text-[9px] text-mute uppercase font-bold mb-1">Cash Engine (ROIC)</span>
                                <span class="text-white font-bold text-xl">
                                    <?php echo number_format($row['roic_current'], 1); ?>%
                                </span>
                            </div>
                            <div class="bg-[#0f1218] p-3 rounded border border-gray-800/50">
                                <span class="block text-[9px] text-mute uppercase font-bold mb-1">FCF Yield</span>
                                <span class="text-accent font-bold text-xl"><?php echo number_format($row['fcf_yield'], 1); ?>%</span>
                            </div>
                        </div>
                        
                        <?php if($row['lie_detector_status'] == 'SUSPICIOUS'): ?>
                            <div class="mb-4 bg-red-500/10 border border-red-500/30 p-2 rounded flex items-center gap-2">
                                <span class="text-red-500">⚠️</span>
                                <span class="text-[10px] text-red-200 font-bold uppercase">Accounting Mismatch Detected</span>
                            </div>
                        <?php endif; ?>

                        <div class="space-y-4 border-t border-gray-800 pt-5">
                            <div>
                                <div class="flex justify-between text-[10px] uppercase font-bold text-mute mb-1">
                                    <span>Balance Sheet Safety</span><span><?php echo $row['safety_score']; ?>/100</span>
                                </div>
                                <div class="h-2 w-full bg-gray-800 rounded-full overflow-hidden">
                                    <div class="h-full bg-blue-500" style="width: <?php echo $row['safety_score']; ?>%"></div>
                                </div>
                            </div>
                            <div>
                                <div class="flex justify-between text-[10px] uppercase font-bold text-mute mb-1">
                                    <span>Quality Score</span><span class="text-accent"><?php echo $row['cash_engine_score']; ?>/100</span>
                                </div>
                                <div class="h-2 w-full bg-gray-800 rounded-full overflow-hidden">
                                    <div class="h-full bg-accent shadow-[0_0_10px_rgba(0,209,133,0.5)]" style="width: <?php echo $row['cash_engine_score']; ?>%"></div>
                                </div>
                            </div>
                        </div>

                    </div>
                <?php endwhile; ?>
            </div>
        <?php else: ?>
             <div class="p-10 border border-dashed border-gray-700 rounded text-center text-mute">
                NO ASSETS PASSED THE FILTER. MARKET IS OVERHEATED.
             </div>
        <?php endif; ?>
    </div>

    <div class="mb-16">
        <div class="flex items-center gap-4 mb-6">
            <h2 class="text-danger text-sm font-bold uppercase tracking-[0.2em] border-l-4 border-danger pl-4">
                Rejected / High Risk
            </h2>
            <div class="h-px bg-gray-800 flex-grow"></div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <?php while($row = $res_rejected->fetch_assoc()): ?>
                <div class="bg-panel border border-white/5 p-4 rounded hover:border-danger/30 transition-colors group">
                    <div class="flex justify-between items-center mb-3">
                        <span class="font-black text-lg text-gray-500 group-hover:text-gray-200"><?php echo $row['ticker']; ?></span>
                        <span class="text-[9px] font-bold text-danger bg-danger/10 px-2 py-0.5 rounded border border-danger/20">FAIL</span>
                    </div>
                    <div class="text-[11px] text-red-400 font-mono leading-relaxed opacity-80">
                        <?php 
                            $reasons = explode('|', $row['failure_reasons']);
                            foreach($reasons as $reason) {
                                echo "<div class='mb-1 flex items-start gap-2'><span class='text-danger'>×</span> <span>".trim($reason)."</span></div>";
                            }
                        ?>
                    </div>
                </div>
            <?php endwhile; ?>
        </div>
    </div>

    <footer class="border-t border-gray-800 pt-10 pb-20">
        <h3 class="text-white text-xs font-bold uppercase tracking-widest mb-6">Algorithm Logic & Methodology</h3>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
            
            <div>
                <h4 class="text-accent text-sm font-bold mb-2">Safety Score</h4>
                <p class="text-[11px] text-mute leading-5">
                    Measures the risk of bankruptcy. Evaluates Debt-to-Equity ratio. A score of 100 means zero debt. A score below 50 indicates high leverage and fragility in a recession.
                </p>
            </div>

            <div>
                <h4 class="text-accent text-sm font-bold mb-2">Cash Engine</h4>
                <p class="text-[11px] text-mute leading-5">
                    A composite of ROIC (Return on Invested Capital) and Gross Margins. This measures how efficiently management turns $1 of capital into profit.
                </p>
            </div>

            <div>
                <h4 class="text-accent text-sm font-bold mb-2">Valuation Zones</h4>
                <ul class="text-[11px] text-mute leading-5 space-y-1">
                    <li><span class="text-emerald-400">BARGAIN:</span> FCF Yield > 8%</li>
                    <li><span class="text-amber-400">FAIR:</span> FCF Yield 4.5% - 8%</li>
                    <li><span class="text-rose-400">PRICEY:</span> FCF Yield < 4.5%</li>
                </ul>
            </div>

            <div>
                <h4 class="text-accent text-sm font-bold mb-2">The "Lie Detector"</h4>
                <p class="text-[11px] text-mute leading-5">
                    Compares Net Income (Accounting Profit) to Free Cash Flow (Real Cash). If Net Income is high but Cash Flow is low, the company may be manipulating earnings.
                </p>
            </div>

        </div>
    </footer>

</body>
</html>