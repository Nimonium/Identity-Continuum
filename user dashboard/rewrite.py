import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove profile and settings nav links
content = re.sub(r'<button id=nav-profile.*?</button>\s*', '', content, flags=re.DOTALL)
content = re.sub(r'<button id=nav-settings.*?</button>\s*', '', content, flags=re.DOTALL)

# 2. Update screen-signin
signin_new = r'''<section id=screen-signin class=screen relative items-center justify-center bg-base overflow-hidden p-6>
            <!-- Dynamic Background -->
            <div class=absolute inset-0 z-0 pointer-events-none overflow-hidden>
                <div class=absolute -top-[20%] -right-[10%] w-[800px] h-[800px] bg-primary/5 rounded-full blur-[120px]></div>
                <div class=absolute top-[40%] -left-[10%] w-[600px] h-[600px] bg-[#32B0F4]/10 rounded-full blur-[100px]></div>
            </div>
            
            <button class=absolute top-6 left-6 text-ink/50 hover:text-ink z-50 data-nav=screen-landing>
                <i data-lucide=arrow-left class=w-6 h-6></i>
            </button>
            
            <div class=w-full max-w-6xl relative z-10 grid grid-cols-1 lg:grid-cols-2 bg-white rounded-[2rem] shadow-2xl border border-hairline overflow-hidden>
                <!-- Image Side -->
                <div class=hidden lg:block relative bg-ink>
                    <img src=signin-image.jpg alt=Security Gate class=absolute inset-0 w-full h-full object-cover opacity-90>
                    <div class=absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent></div>
                    <div class=absolute bottom-10 left-10 right-10 text-white>
                        <h2 class=text-3xl font-display font-semibold mb-2>Fast-track your journey</h2>
                        <p class=text-white/80>Secure biometric verification for modern travelers.</p>
                    </div>
                </div>
                <!-- Form Side -->
                <div class=p-10 md:p-16 flex flex-col justify-center>
                    <div class=text-center mb-10>
                        <i data-lucide=scan-face class=w-12 h-12 text-primary mx-auto mb-4></i>
                        <h2 class=font-display text-xl tracking-wide uppercase font-bold text-ink/80 mb-2>Identity Continuum</h2>
                        <h3 class=text-3xl font-semibold>Welcome back</h3>
                        <p class=text-ink/60 mt-2>Sign in to your traveler account</p>
                    </div>
                    <form class=space-y-6 onsubmit=event.preventDefault(); document.querySelector('[data-nav=\'screen-dashboard\']').click();>
                        <div>
                            <label class=block text-xs uppercase tracking-wider font-semibold text-ink/60 mb-2>Email Address</label>
                            <input type=email placeholder=you@example.com class=form-input w-full py-3 text-base value=alex.chen@example.com>
                        </div>
                        <div>
                            <label class=block text-xs uppercase tracking-wider font-semibold text-ink/60 mb-2>Password</label>
                            <input type=password placeholder=•••••••• class=form-input w-full py-3 text-base value=password123>
                        </div>
                        <button type=submit class=btn-primary w-full py-3 text-lg mt-4 shadow-lg shadow-primary/20 data-nav=screen-dashboard>Sign In</button>
                    </form>
    
                    <div class=mt-8 mb-8 flex items-center justify-center>
                        <div class=h-px bg-hairline flex-grow></div>
                        <span class=px-4 text-xs uppercase font-semibold text-ink/40 tracking-wider>or continue with</span>
                        <div class=h-px bg-hairline flex-grow></div>
                    </div>
                    
                    <div class=grid grid-cols-2 gap-4>
                        <button class=btn-outline w-full flex items-center justify-center gap-3 py-3 hover:bg-black/5 data-nav=screen-dashboard>
                            <svg class=w-5 h-5 viewBox=0 0 24 24><path fill=#4285F4 d=M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z/><path fill=#34A853 d=M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z/><path fill=#FBBC05 d=M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z/><path fill=#EA4335 d=M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z/></svg>
                            Google
                        </button>
                        <button class=btn-outline w-full flex items-center justify-center gap-3 py-3 hover:bg-black/5 data-nav=screen-dashboard>
                            <i data-lucide=fingerprint class=w-5 h-5 text-primary></i>
                            DigiLocker
                        </button>
                    </div>
                </div>
            </div>
        </section>'''
content = re.sub(r'<section id=screen-signin.*?</section>', signin_new, content, flags=re.DOTALL)

# 3. Update dashboard screen wrapper
dash_new = r'''<section id=screen-dashboard class=screen p-6 md:p-12 max-w-7xl mx-auto w-full space-y-12 relative overflow-hidden>
            <!-- Dynamic Background -->
            <div class=absolute inset-0 z-0 pointer-events-none overflow-hidden>
                <div class=absolute -top-40 right-0 w-[600px] h-[600px] bg-[#32B0F4]/5 rounded-full blur-[100px]></div>
            </div>
            <div class=relative z-10 space-y-12 w-full>
'''
content = re.sub(r'<section id=screen-dashboard class=.*?>', dash_new, content)
content = re.sub(r'(</section>\s*<!-- ==============================================\s*<!-- SCREEN 5: VERIFY FLOW)', r'</div>\1', content) # close the relative div

# 4. Update verify screen wrapper
verify_new = r'''<section id=screen-verify class=screen p-6 md:p-12 max-w-6xl mx-auto w-full relative overflow-hidden>
            <!-- Dynamic Background -->
            <div class=absolute inset-0 z-0 pointer-events-none overflow-hidden>
                <div class=absolute bottom-0 left-0 w-[500px] h-[500px] bg-primary/5 rounded-full blur-[120px]></div>
            </div>
            <div class=relative z-10 w-full>
'''
content = re.sub(r'<section id=screen-verify class=.*?>', verify_new, content)
content = re.sub(r'(</section>\s*<!-- ==============================================\s*<!-- SCREEN 6: RESULT)', r'</div>\1', content) # close relative div

# 5. Remove profile and settings sections entirely
content = re.sub(r'<!-- ==============================================\s*<!-- SCREEN 4: PROFILE.*?<!-- ==============================================.*?<!-- SCREEN 5', r'<!-- ============================================== <!-- SCREEN 5', content, flags=re.DOTALL)
content = re.sub(r'<!-- ==============================================\s*<!-- SCREEN 7: SETTINGS.*?</section>', '', content, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print( done)
