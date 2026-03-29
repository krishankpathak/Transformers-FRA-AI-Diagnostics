import io, base64
import numpy as np
import pandas as pd
import os

def get_base64(fig):
    import matplotlib.pyplot as plt
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode()

def plot_single_curve(freq, mag, title="FRA Sweep"):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(freq, mag, color='#0ea5e9', linewidth=2)
    ax.set_xscale('log')
    ax.set_title(title, color='white', pad=20)
    ax.set_xlabel('Frequency (Hz)', color='#94a3b8')
    ax.set_ylabel('Magnitude (dB)', color='#94a3b8')
    ax.grid(True, which="both", ls="-", alpha=0.1)
    
    # Style
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')
    ax.tick_params(colors='#94a3b8')
    for spine in ax.spines.values():
        spine.set_color('#1e293b')
        
    return get_base64(fig)

def plot_comparison(freq, mag, baseline_mag):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(freq, baseline_mag, label='Reference', color='#94a3b8', alpha=0.6, linestyle='--')
    ax.plot(freq, mag, label='Test', color='#0ea5e9', linewidth=2)
    ax.set_xscale('log')
    ax.set_title("Comparison: Reference vs Test", color='white', pad=20)
    ax.legend()
    
    # Style
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')
    ax.tick_params(colors='#94a3b8')
    for spine in ax.spines.values():
        spine.set_color('#1e293b')
        
    return get_base64(fig)

def plot_difference(freq, mag, baseline_mag):
    import matplotlib.pyplot as plt
    diff = mag - baseline_mag
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.fill_between(freq, diff, color='#ef4444', alpha=0.3)
    ax.plot(freq, diff, color='#ef4444', linewidth=1)
    ax.axhline(0, color='white', alpha=0.2)
    ax.set_xscale('log')
    ax.set_title("Magnitude Difference (dB)", color='white', pad=20)
    
    # Style
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')
    ax.tick_params(colors='#94a3b8')
    for spine in ax.spines.values():
        spine.set_color('#1e293b')
        
    return get_base64(fig)

def plot_3d_surface(freq, mag):
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib import cm
    
    # Create a 3D surface plot by simulating a series of curves or using 2D grid
    # For a single curve, we can create a "ribbon" or a surface by replicating it.
    
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    # Create meshgrid
    X = np.log10(freq)
    Y = np.arange(0, 10, 1) # 10 slices for surface
    X, Y = np.meshgrid(X, Y)
    
    # Replicate mag for surface
    Z = np.tile(mag, (10, 1))
    
    # Add some variation to Y slices for better 3D effect
    for i in range(10):
        Z[i] = Z[i] + np.random.normal(0, 0.1 * i, size=len(mag))
    
    # Use standard colormap access
    from matplotlib import colormaps
    cmap = colormaps.get_cmap('viridis')
    
    surf = ax.plot_surface(X, Y, Z, cmap=cmap, linewidth=0, antialiased=True, alpha=0.8)
    
    ax.set_title("3D Frequency Response Surface", color='white', pad=20)
    ax.set_xlabel('Log Frequency (Hz)', color='#94a3b8')
    ax.set_ylabel('Sample Slice', color='#94a3b8')
    ax.set_zlabel('Magnitude (dB)', color='#94a3b8')
    
    # Style - Fix Axes3D attribute errors (w_xaxis -> xaxis)
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')
    ax.xaxis.set_pane_color((0.05, 0.09, 0.16, 1.0)) # type: ignore
    ax.yaxis.set_pane_color((0.05, 0.09, 0.16, 1.0)) # type: ignore
    ax.zaxis.set_pane_color((0.05, 0.09, 0.16, 1.0)) # type: ignore
    ax.tick_params(colors='#94a3b8')
    
    return get_base64(fig)

def generate_all_plots(freq, mag):
    import matplotlib
    matplotlib.use('Agg')
    # Load baseline for comparison
    # Use relative path or pass PROJECT_ROOT if possible. For now, try relative.
    baseline_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw", "fra_healthy.csv")
    if os.path.exists(baseline_path):
        try:
            df = pd.read_csv(baseline_path)
            # Interpolate baseline to match test freq
            baseline_mag = np.interp(
                freq, 
                df["Frequency"].to_numpy().astype(float), 
                df["Magnitude"].to_numpy().astype(float)
            )
        except:
            baseline_mag = mag
    else:
        baseline_mag = mag
        
    p1 = plot_single_curve(freq, mag)
    p2 = plot_comparison(freq, mag, baseline_mag)
    p3 = plot_difference(freq, mag, baseline_mag)
    p4 = plot_3d_surface(freq, mag)
    
    return p1, p2, p3, p4