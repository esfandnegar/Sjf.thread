import threading
import queue

# --- Thread 1: محاسبه زمان انتظار ---
class WaitingTimeThread(threading.Thread):
    def __init__(self, q_in, q_out):
        super().__init__()
        self.q_in = q_in
        self.q_out = q_out

    def run(self):
        while True:
            item = self.q_in.get()
            if item is None:
                self.q_out.put(None)
                break

            processes, n, bt, at = item
            wt = [0] * n
            rt = bt.copy()
            complete = 0
            t = 0
            minm = 999999999
            short = 0
            check = False

            while complete != n:
                for j in range(n):
                    if (at[j] <= t) and (rt[j] < minm) and (rt[j] > 0):
                        minm = rt[j]
                        short = j
                        check = True
                if not check:
                    t += 1
                    continue

                rt[short] -= 1
                minm = rt[short]
                if minm == 0:
                    minm = 999999999

                if rt[short] == 0:
                    complete += 1
                    check = False
                    fint = t + 1
                    wt[short] = fint - bt[short] - at[short]
                    if wt[short] < 0:
                        wt[short] = 0
                t += 1

            self.q_out.put((processes, n, bt, at, wt))
            self.q_in.task_done()


# --- Thread 2: محاسبه زمان گردش ---
class TurnaroundTimeThread(threading.Thread):
    def __init__(self, q_in, q_out):
        super().__init__()
        self.q_in = q_in
        self.q_out = q_out

    def run(self):
        while True:
            item = self.q_in.get()
            if item is None:
                break

            processes, n, bt, at, wt = item
            tat = [bt[i] + wt[i] for i in range(n)]
            self.q_out.put((processes, n, bt, at, wt, tat))
            self.q_in.task_done()


# --- Main ---
if __name__ == "__main__":
    n = int(input("Enter number of processes: "))
    processes = [i + 1 for i in range(n)]
    burst_time = []
    arrival_time = []

    for i in range(n):
        at = int(input(f"Enter Arrival Time for Process P{i + 1}: "))
        bt = int(input(f"Enter Burst Time for Process P{i + 1}: "))
        arrival_time.append(at)
        burst_time.append(bt)

    # --- صف‌ها ---
    q1 = queue.Queue()
    q2 = queue.Queue()
    q3 = queue.Queue()

    # --- ساخت و استارت تردها ---
    t1 = WaitingTimeThread(q1, q2)
    t2 = TurnaroundTimeThread(q2, q3)
    t1.start()
    t2.start()

    # --- ارسال داده به Thread 1 ---
    q1.put((processes, n, burst_time, arrival_time))
    q1.put(None)  # سیگنال پایان

    # --- منتظر پایان ---
    result = q3.get()

    # --- چاپ نتیجه ---
    if result:
        processes, n, bt, at, wt, tat = result
        print("\n--- SJF (Preemptive) Scheduling using Two Threads ---")
        print("Process\tAT\tBT\tWT\tTAT")
        for i in range(n):
            print(f"P{processes[i]}\t{at[i]}\t{bt[i]}\t{wt[i]}\t{tat[i]}")

        print(f"\nAverage Waiting Time: {sum(wt)/n:.2f}")
        print(f"Average Turnaround Time: {sum(tat)/n:.2f}")

    # --- بستن ---
    q2.put(None)
    t1.join()
    t2.join()