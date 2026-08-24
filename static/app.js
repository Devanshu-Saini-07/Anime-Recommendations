(function () {
    const body = document.body;
    const navToggle = document.querySelector("[data-menu-toggle]");
    const navMenu = document.querySelector("[data-nav-menu]");
    const swordCursor = document.querySelector("[data-sword-cursor]");
    const revealElements = document.querySelectorAll(".reveal");
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const canUseCustomCursor = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
    const canUseMoonScene = canUseCustomCursor && !prefersReducedMotion && body.classList.contains("authenticated-app");

    if (navToggle && navMenu) {
        navToggle.addEventListener("click", function () {
            const isOpen = navMenu.classList.toggle("is-open");
            navToggle.setAttribute("aria-expanded", String(isOpen));
        });
    }

    document.querySelectorAll("[data-password-toggle]").forEach(function (button) {
        button.addEventListener("click", function () {
            const targetId = button.getAttribute("data-target");
            const input = document.getElementById(targetId);
            if (!input) {
                return;
            }

            const nextType = input.type === "password" ? "text" : "password";
            input.type = nextType;
            button.textContent = nextType === "password" ? "Show" : "Hide";
        });
    });

    document.querySelectorAll("[data-scroll-target]").forEach(function (button) {
        button.addEventListener("click", function (event) {
            const selector = button.getAttribute("data-scroll-target");
            const target = selector ? document.querySelector(selector) : null;
            if (!target) {
                return;
            }

            event.preventDefault();
            target.scrollIntoView({ behavior: prefersReducedMotion ? "auto" : "smooth", block: "start" });
        });
    });

    if (!prefersReducedMotion && "IntersectionObserver" in window) {
        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12 });

        revealElements.forEach(function (element) {
            observer.observe(element);
        });
    } else {
        revealElements.forEach(function (element) {
            element.classList.add("is-visible");
        });
    }

    initSwordCursor();

    if (canUseMoonScene) {
        initMoonBreathing();
    }

    function initSwordCursor() {
        if (!canUseCustomCursor || !swordCursor || !body.classList.contains("auth-page")) {
            return;
        }

        const isAuthPage = body.classList.contains("auth-page");
        const interactiveSelector = [
            "header",
            "button",
            "a[href]",
            "input",
            "select",
            "textarea",
            "label",
            ".glass-panel",
            ".anime-card",
            ".recommendation-card",
            ".genre-card",
            "[role='button']",
            "[data-menu-toggle]"
        ].join(", ");
        let swordVisible = isAuthPage;
        let renderedSwordVisible;
        let pointerX = window.innerWidth / 2;
        let pointerY = window.innerHeight / 2;
        let swordX = pointerX;
        let swordY = pointerY;
        let cursorAnimationId = null;

        function renderVisibility() {
            if (renderedSwordVisible !== swordVisible) {
                body.classList.toggle("cursor-sword", swordVisible);
                swordCursor.classList.toggle("is-active", swordVisible);
                renderedSwordVisible = swordVisible;
            }

            if (swordVisible && cursorAnimationId === null) {
                cursorAnimationId = window.requestAnimationFrame(animate);
            } else if (!swordVisible && cursorAnimationId !== null) {
                window.cancelAnimationFrame(cursorAnimationId);
                cursorAnimationId = null;
            }
        }

        function setVisibilityFromTarget(target) {
            if (isAuthPage) {
                swordVisible = true;
            } else {
                swordVisible = !Boolean(target && target.closest && target.closest(interactiveSelector));
            }
            renderVisibility();
        }

        function animate() {
            cursorAnimationId = null;
            if (!swordVisible) {
                return;
            }
            swordX += (pointerX - swordX) * 0.22;
            swordY += (pointerY - swordY) * 0.22;
            swordCursor.style.transform = "translate(" + (swordX - 12) + "px, " + (swordY - 12) + "px)";
            cursorAnimationId = window.requestAnimationFrame(animate);
        }

        window.addEventListener("mousemove", function (event) {
            pointerX = event.clientX;
            pointerY = event.clientY;
            setVisibilityFromTarget(event.target);
        });

        window.addEventListener("mouseenter", function () {
            renderVisibility();
        });

        document.addEventListener("mouseleave", function () {
            if (!isAuthPage) {
                swordVisible = false;
                renderVisibility();
            }
        });

        document.addEventListener("focusin", function (event) {
            setVisibilityFromTarget(event.target);
        });

        renderVisibility();
        animate();
    }

    function initMoonBreathing() {
        const canvas = document.getElementById("moonBreathingCanvas");
        const hdCanvas = document.getElementById("moonBreathingHd");
        const bg = document.getElementById("moonBreathingBg");
        if (!canvas || !hdCanvas || !bg) {
            return;
        }

        const ctx = canvas.getContext("2d");
        const hctx = hdCanvas.getContext("2d");
        let W = 0;
        let H = 0;
        let dpr = 1;
        let lastFrame = performance.now();
        let ambE = 0;
        let ambF = 0;
        let ambC = 0;
        let ambHD = 0;
        let animationFrameId = null;

        const lerp = (a, b, t) => a + (b - a) * t;
        const rand = (a, b) => a + Math.random() * (b - a);
        const randi = (a, b) => (a + Math.random() * (b - a)) | 0;
        const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
        const TAU = Math.PI * 2;

        const LUT_R = new Uint8Array(256);
        const LUT_G = new Uint8Array(256);
        const LUT_B = new Uint8Array(256);
        buildLut(LUT_R, LUT_G, LUT_B, [
            [0, [0, 0, 0]],
            [30, [20, 0, 40]],
            [70, [60, 0, 90]],
            [110, [110, 10, 160]],
            [150, [160, 30, 200]],
            [195, [200, 80, 240]],
            [230, [220, 160, 255]],
            [255, [240, 230, 255]]
        ]);

        const BLUT_R = new Uint8Array(256);
        const BLUT_G = new Uint8Array(256);
        const BLUT_B = new Uint8Array(256);
        buildLut(BLUT_R, BLUT_G, BLUT_B, [
            [0, [0, 0, 0]],
            [50, [40, 0, 10]],
            [100, [120, 5, 20]],
            [160, [200, 20, 40]],
            [210, [240, 60, 80]],
            [255, [255, 140, 160]]
        ]);

        function buildLut(rOut, gOut, bOut, stops) {
            for (let i = 0; i < 256; i += 1) {
                for (let s = 0; s < stops.length - 1; s += 1) {
                    const t0 = stops[s][0];
                    const c0 = stops[s][1];
                    const t1 = stops[s + 1][0];
                    const c1 = stops[s + 1][1];
                    if (i >= t0 && i <= t1) {
                        const f = (i - t0) / (t1 - t0);
                        rOut[i] = (c0[0] + (c1[0] - c0[0]) * f) | 0;
                        gOut[i] = (c0[1] + (c1[1] - c0[1]) * f) | 0;
                        bOut[i] = (c0[2] + (c1[2] - c0[2]) * f) | 0;
                        break;
                    }
                }
            }
        }

        function moonColor(t, a) {
            const i = clamp(t * 255, 0, 255) | 0;
            return "rgba(" + LUT_R[i] + "," + LUT_G[i] + "," + LUT_B[i] + "," + a + ")";
        }

        function bloodColor(t, a) {
            const i = clamp(t * 255, 0, 255) | 0;
            return "rgba(" + BLUT_R[i] + "," + BLUT_G[i] + "," + BLUT_B[i] + "," + a + ")";
        }

        const P = {
            x: window.innerWidth / 2,
            y: window.innerHeight / 2,
            tx: window.innerWidth / 2,
            ty: window.innerHeight / 2,
            px: window.innerWidth / 2,
            py: window.innerHeight / 2,
            vx: 0,
            vy: 0,
            speed: 0,
            lastMove: performance.now()
        };

        function resize() {
            dpr = Math.min(window.devicePixelRatio || 1, 2);
            W = window.innerWidth;
            H = window.innerHeight;
            canvas.width = W * dpr;
            canvas.height = H * dpr;
            canvas.style.width = W + "px";
            canvas.style.height = H + "px";
            ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
            hdCanvas.width = W * dpr;
            hdCanvas.height = H * dpr;
            hdCanvas.style.width = W + "px";
            hdCanvas.style.height = H + "px";
            hctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        }

        function setTarget(x, y) {
            P.tx = x;
            P.ty = y;
            P.lastMove = performance.now();
        }

        const embers = makePool(600);
        const smoke = makePool(300);
        const flames = makePool(350);
        const crescents = makePool(120);
        const sparks = makePool(400, function () {
            return { alive: false, px: 0, py: 0 };
        });
        const moonBlades = makePool(60);
        const hdCells = makePool(200);
        const waves = [];
        const flashes = [];
        const trail = [];

        function makePool(size, factory) {
            const pool = [];
            for (let i = 0; i < size; i += 1) {
                pool.push(factory ? factory() : { alive: false });
            }
            pool.head = 0;
            return pool;
        }

        function take(pool) {
            const item = pool[pool.head % pool.length];
            pool.head += 1;
            return item;
        }

        function spawnEmber(x, y, vx, vy, life, sz, hot, blood) {
            const e = take(embers);
            e.alive = true;
            e.x = x;
            e.y = y;
            e.vx = vx;
            e.vy = vy;
            e.age = 0;
            e.life = life;
            e.sz = sz;
            e.hot = hot;
            e.sway = rand(0.3, 1.2);
            e.phase = rand(0, TAU);
            e.grav = rand(-20, 15);
            e.blood = Boolean(blood);
            e.rot = rand(0, TAU);
            e.rotSpd = rand(-2, 2);
        }

        function spawnSmoke(x, y, vx, vy, r, life, dark) {
            const s = take(smoke);
            s.alive = true;
            s.x = x;
            s.y = y;
            s.vx = vx;
            s.vy = vy;
            s.age = 0;
            s.life = life;
            s.r = r;
            s.dark = Boolean(dark);
        }

        function spawnFlame(x, y, vx, vy, r, life, hot, blood) {
            const f = take(flames);
            f.alive = true;
            f.x = x;
            f.y = y;
            f.vx = vx;
            f.vy = vy;
            f.age = 0;
            f.life = life;
            f.r = r;
            f.hot = hot;
            f.blood = Boolean(blood);
        }

        function spawnCrescent(x, y, angle, speed, r, life, hot, blood) {
            const c = take(crescents);
            c.alive = true;
            c.x = x;
            c.y = y;
            c.vx = Math.cos(angle) * speed;
            c.vy = Math.sin(angle) * speed;
            c.angle = angle;
            c.r = r;
            c.age = 0;
            c.life = life;
            c.hot = hot;
            c.blood = Boolean(blood);
            c.spin = rand(-3, 3);
        }

        function spawnSpark(x, y, vx, vy, life, bright, blood) {
            const s = take(sparks);
            s.alive = true;
            s.x = x;
            s.y = y;
            s.px = x;
            s.py = y;
            s.vx = vx;
            s.vy = vy;
            s.age = 0;
            s.life = life;
            s.bright = bright;
            s.blood = Boolean(blood);
        }

        function spawnMoonBlade(x, y, angle, speed, r, life, tier, waveIdx) {
            const b = take(moonBlades);
            b.alive = true;
            b.x = x;
            b.y = y;
            b.vx = Math.cos(angle) * speed;
            b.vy = Math.sin(angle) * speed;
            b.angle = angle;
            b.r = r;
            b.age = 0;
            b.life = life;
            b.tier = tier || 0;
            b.waveDelay = (waveIdx || 0) * 38;
            b.waveActive = false;
            b.spin = rand(-0.8, 0.8);
            b.arcDrift = rand(-0.012, 0.012);
            b.veinSeed = rand(0, TAU);
            b.trailX = x;
            b.trailY = y;
            b.trailPoints = [];
        }

        function spawnHD(x, y, str, life) {
            const h = take(hdCells);
            h.alive = true;
            h.x = x;
            h.y = y;
            h.str = str;
            h.age = 0;
            h.life = life;
        }

        function addTrail(x, y, now) {
            trail.push({ x: x, y: y, t: now });
            while (trail.length > 70) {
                trail.shift();
            }
        }

        function burst(x, y) {
            waves.push({ x: x, y: y, r: 0, maxR: rand(200, 300), age: 0, life: 700 });
            flashes.push({ x: x, y: y, r: 0, maxR: rand(260, 400), age: 0, life: 550 });

            for (let i = 0; i < 18; i += 1) {
                const a = i / 18 * TAU + rand(-0.12, 0.12);
                const spd = rand(140, 400);
                const isBlood = Math.random() < 0.3;
                spawnCrescent(x, y, a, spd, rand(18, 45), rand(450, 850), rand(0.7, 1.0), isBlood);
                spawnFlame(x, y, Math.cos(a) * spd * 0.5, Math.sin(a) * spd * 0.5, rand(22, 48), rand(350, 700), rand(0.6, 1.0), isBlood);
                if (i % 2 === 0) {
                    spawnSmoke(x + rand(-8, 8), y + rand(-8, 8), Math.cos(a) * spd * 0.18, Math.sin(a) * spd * 0.18 - rand(25, 55), rand(20, 38), rand(550, 850), true);
                }
            }

            for (let i = 0; i < 140; i += 1) {
                const a = rand(0, TAU);
                const spd = rand(90, 520);
                const isBlood = Math.random() < 0.25;
                spawnSpark(x, y, Math.cos(a) * spd, Math.sin(a) * spd, rand(280, 950), rand(0.7, 1.0), isBlood);
            }

            for (let i = 0; i < 90; i += 1) {
                const a = rand(0, TAU);
                const spd = rand(35, 210);
                const isBlood = Math.random() < 0.2;
                spawnEmber(x, y, Math.cos(a) * spd, Math.sin(a) * spd - rand(40, 110), rand(500, 1300), rand(1.5, 3.5), rand(0.5, 1.0), isBlood);
            }

            spawnHD(x, y, rand(9, 15), rand(600, 1000));

            for (let i = 0; i < 4; i += 1) {
                spawnMoonBlade(x, y, i / 4 * TAU + rand(-0.14, 0.14), rand(230, 310), rand(44, 58), rand(700, 950), 0, i);
            }

            for (let i = 0; i < 6; i += 1) {
                spawnMoonBlade(x, y, i / 6 * TAU + Math.PI / 6 + rand(-0.18, 0.18), rand(310, 420), rand(28, 40), rand(560, 780), 1, i);
            }

            for (let i = 0; i < 5; i += 1) {
                spawnMoonBlade(x, y, i / 5 * TAU + rand(-0.22, 0.22), rand(420, 560), rand(16, 24), rand(420, 640), 2, i);
            }
        }

        function drawCrescent(cx, cy, r, angle, hot, blood, alpha) {
            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(angle);
            ctx.beginPath();
            ctx.arc(0, 0, r, 0.2, Math.PI - 0.2);
            ctx.arc(r * 0.38, 0, r * 0.72, Math.PI - 0.25, 0.25, true);
            ctx.closePath();
            const colorFn = blood ? bloodColor : moonColor;
            const g = ctx.createRadialGradient(0, 0, 0, 0, 0, r);
            g.addColorStop(0, colorFn(hot, alpha));
            g.addColorStop(0.6, colorFn(hot * 0.7, alpha * 0.6));
            g.addColorStop(1, colorFn(hot * 0.4, 0));
            ctx.fillStyle = g;
            ctx.fill();
            ctx.restore();
        }

        function drawMoonBlade(b, alpha) {
            const tp = b.age / b.life;
            const r = b.r * (1 + tp * 0.14);
            ctx.save();
            ctx.translate(b.x, b.y);
            ctx.rotate(b.angle + Math.PI * 0.5);

            const glowR = r * 2.6;
            const glowG = ctx.createRadialGradient(0, 0, 0, 0, 0, glowR);
            glowG.addColorStop(0, "rgba(180,8,22," + alpha * 0.28 + ")");
            glowG.addColorStop(0.4, "rgba(120,0,18," + alpha * 0.14 + ")");
            glowG.addColorStop(1, "rgba(0,0,0,0)");
            ctx.fillStyle = glowG;
            ctx.beginPath();
            ctx.arc(0, 0, glowR, 0, TAU);
            ctx.fill();

            const arcStart = -Math.PI * 0.72;
            const arcEnd = Math.PI * 0.72;
            const innerOffX = r * 0.44;
            const innerR = r * 0.68;

            ctx.beginPath();
            ctx.arc(0, 0, r, arcStart, arcEnd);
            ctx.arc(innerOffX, 0, innerR, arcEnd - 0.08, arcStart + 0.08, true);
            ctx.closePath();

            const fillG = ctx.createLinearGradient(-r, -r * 0.5, r * 0.6, r * 0.5);
            fillG.addColorStop(0, "rgba(6,0,4," + alpha * 0.95 + ")");
            fillG.addColorStop(0.18, "rgba(90,2,10," + alpha * 0.98 + ")");
            fillG.addColorStop(0.42, "rgba(190,10,28," + alpha + ")");
            fillG.addColorStop(0.65, "rgba(230,22,40," + alpha * 0.95 + ")");
            fillG.addColorStop(0.82, "rgba(160,8,20," + alpha * 0.88 + ")");
            fillG.addColorStop(1, "rgba(20,0,6," + alpha * 0.72 + ")");
            ctx.fillStyle = fillG;
            ctx.fill();

            ctx.beginPath();
            ctx.arc(0, 0, r, arcStart, arcEnd);
            ctx.lineWidth = Math.max(0.5, r * 0.045 * (1 - tp * 0.4));
            ctx.strokeStyle = "rgba(255,140,155," + alpha * 0.88 + ")";
            ctx.stroke();

            ctx.restore();
        }

        function frame(now) {
            animationFrameId = null;
            const dt = Math.min(33, now - lastFrame || 16);
            const dtS = dt / 1000;
            lastFrame = now;

            P.px = P.x;
            P.py = P.y;
            P.x = lerp(P.x, P.tx, 0.16);
            P.y = lerp(P.y, P.ty, 0.16);
            P.vx = (P.x - P.px) / Math.max(dtS, 0.001);
            P.vy = (P.y - P.py) / Math.max(dtS, 0.001);
            P.speed = Math.hypot(P.vx, P.vy);

            bg.style.transform = "translate(" + ((P.tx / W - 0.5) * -32) + "px," + ((P.ty / H - 0.5) * -32) + "px) scale(1.08)";

            addTrail(P.x, P.y, now);
            while (trail.length && now - trail[0].t > 380) {
                trail.shift();
            }

            const moving = now - P.lastMove < 120;
            const speedFactor = clamp(P.speed / 300, 0, 1);

            ambE -= dt;
            if (ambE <= 0) {
                ambE = moving ? rand(8, 22) : rand(28, 55);
                const count = moving ? randi(2, 5) : 1;
                for (let i = 0; i < count; i += 1) {
                    const a = -Math.PI / 2 + rand(-1.0, 1.0);
                    const spd = rand(15, 70) * (1 + speedFactor * 1.8);
                    spawnEmber(P.x + rand(-5, 5), P.y + rand(-5, 5), Math.cos(a) * spd, Math.sin(a) * spd - rand(15, 45), rand(700, 1600), rand(1.0, 2.8), rand(0.4, 0.9), Math.random() < 0.1);
                }
            }

            ambF -= dt;
            if (ambF <= 0) {
                ambF = moving ? rand(10, 25) : rand(30, 65);
                const count = moving ? randi(2, 6) : randi(1, 3);
                for (let i = 0; i < count; i += 1) {
                    const a = -Math.PI / 2 + rand(-1.1, 1.1);
                    const spd = rand(12, 65) * (1 + speedFactor * 1.4);
                    spawnFlame(P.x + rand(-6, 6), P.y + rand(-6, 6), Math.cos(a) * spd * 0.45, Math.sin(a) * spd - rand(8, 38), rand(9, 26) * (1 + speedFactor * 0.7), rand(160, 380), rand(0.4, 1.0), Math.random() < 0.08);
                }
            }

            ambC -= dt;
            if (ambC <= 0 && moving && P.speed > 40) {
                ambC = rand(60, 140);
                spawnCrescent(P.x + rand(-8, 8), P.y + rand(-8, 8), -Math.PI / 2 + rand(-1.3, 1.3), rand(20, 70), rand(6, 16), rand(350, 700), rand(0.5, 0.9), Math.random() < 0.12);
            }

            ambHD -= dt;
            if (ambHD <= 0) {
                ambHD = rand(90, 170);
                spawnHD(P.x + rand(-18, 18), P.y + rand(-18, 18), rand(3, 6), rand(180, 380));
            }

            ctx.clearRect(0, 0, W, H);
            ctx.globalCompositeOperation = "lighter";

            for (let i = flashes.length - 1; i >= 0; i -= 1) {
                const f = flashes[i];
                f.age += dt;
                if (f.age >= f.life) {
                    flashes.splice(i, 1);
                    continue;
                }
                const tp = f.age / f.life;
                const r = lerp(0, f.maxR, Math.pow(tp, 0.28));
                const a = (1 - tp) * (1 - tp) * 0.32;
                const g = ctx.createRadialGradient(f.x, f.y, 0, f.x, f.y, r);
                g.addColorStop(0, "rgba(220,180,255," + a + ")");
                g.addColorStop(0.25, "rgba(160,60,220," + a * 0.8 + ")");
                g.addColorStop(0.5, "rgba(80,10,140," + a * 0.5 + ")");
                g.addColorStop(0.75, "rgba(120,5,30," + a * 0.25 + ")");
                g.addColorStop(1, "rgba(0,0,0,0)");
                ctx.fillStyle = g;
                ctx.beginPath();
                ctx.arc(f.x, f.y, r, 0, TAU);
                ctx.fill();
            }

            for (let i = waves.length - 1; i >= 0; i -= 1) {
                const w = waves[i];
                w.age += dt;
                if (w.age >= w.life) {
                    waves.splice(i, 1);
                    continue;
                }
                const tp = w.age / w.life;
                const r = lerp(0, w.maxR, Math.pow(tp, 0.5));
                const a = (1 - tp) * (1 - tp) * 0.75;
                const lw = lerp(7, 0.4, tp);

                ctx.beginPath();
                ctx.arc(w.x, w.y, r, 0, TAU);
                ctx.lineWidth = lw;
                ctx.strokeStyle = "rgba(180,80,255," + a + ")";
                ctx.stroke();
            }

            ctx.globalCompositeOperation = "source-over";
            updateSmoke(dt, dtS);
            ctx.globalCompositeOperation = "lighter";
            updateFlames(dt, dtS, now);
            updateCrescents(dt, dtS);
            updateMoonBlades(dt, dtS);
            drawTrail(now);
            updateSparks(dt, dtS);
            updateEmbers(dt, dtS, now);
            drawCursorTip(now);

            ctx.globalCompositeOperation = "source-over";
            drawHd(dt);

            scheduleFrame();
        }

        function scheduleFrame() {
            if (animationFrameId === null && !document.hidden) {
                animationFrameId = window.requestAnimationFrame(frame);
            }
        }

        function stopFrame() {
            if (animationFrameId !== null) {
                window.cancelAnimationFrame(animationFrameId);
                animationFrameId = null;
            }
        }

        function updateSmoke(dt, dtS) {
            for (let i = 0; i < smoke.length; i += 1) {
                const s = smoke[i];
                if (!s.alive) {
                    continue;
                }
                s.age += dt;
                if (s.age >= s.life) {
                    s.alive = false;
                    continue;
                }
                s.x += s.vx * dtS;
                s.y += s.vy * dtS;
                s.vy -= dtS * 6;
                const tp = s.age / s.life;
                const r = s.r * (1 + tp * 1.3);
                const a = (1 - tp) * (s.dark ? 0.16 : 0.09) * Math.sin(tp * Math.PI);
                const g = ctx.createRadialGradient(s.x, s.y, 0, s.x, s.y, Math.max(1, r));
                g.addColorStop(0, s.dark ? "rgba(8,2,18," + a + ")" : "rgba(60,20,100," + a * 0.7 + ")");
                g.addColorStop(1, "rgba(0,0,0,0)");
                ctx.fillStyle = g;
                ctx.beginPath();
                ctx.arc(s.x, s.y, Math.max(1, r), 0, TAU);
                ctx.fill();
            }
        }

        function updateFlames(dt, dtS, now) {
            for (let i = 0; i < flames.length; i += 1) {
                const f = flames[i];
                if (!f.alive) {
                    continue;
                }
                f.age += dt;
                if (f.age >= f.life) {
                    f.alive = false;
                    continue;
                }
                f.x += f.vx * dtS;
                f.y += f.vy * dtS;
                f.vy -= dtS * 42;
                f.vx += Math.sin(now * 0.006 + f.age * 0.009) * dtS * 30;
                const tp = f.age / f.life;
                const hotness = f.hot * (1 - tp);
                const r = f.r * (1 + tp * 0.28);
                const a = Math.sin(tp * Math.PI) * 0.65 * f.hot;
                const g = ctx.createRadialGradient(f.x, f.y, 0, f.x, f.y, Math.max(1, r));
                const colorFn = f.blood ? bloodColor : moonColor;
                g.addColorStop(0, colorFn(hotness, a));
                g.addColorStop(0.45, colorFn(hotness * 0.6, a * 0.65));
                g.addColorStop(0.8, colorFn(hotness * 0.3, a * 0.28));
                g.addColorStop(1, "rgba(0,0,0,0)");
                ctx.fillStyle = g;
                ctx.beginPath();
                ctx.arc(f.x, f.y, Math.max(1, r), 0, TAU);
                ctx.fill();
            }
        }

        function updateCrescents(dt, dtS) {
            for (let i = 0; i < crescents.length; i += 1) {
                const c = crescents[i];
                if (!c.alive) {
                    continue;
                }
                c.age += dt;
                if (c.age >= c.life) {
                    c.alive = false;
                    continue;
                }
                c.x += c.vx * dtS;
                c.y += c.vy * dtS;
                c.vy -= dtS * 18;
                c.angle += c.spin * dtS;
                const tp = c.age / c.life;
                const a = Math.sin(tp * Math.PI) * 0.8 * c.hot;
                if (a > 0.01) {
                    drawCrescent(c.x, c.y, c.r * (1 + tp * 0.2), c.angle, c.hot * (1 - tp), c.blood, a);
                }
            }
        }

        function updateMoonBlades(dt, dtS) {
            for (let i = 0; i < moonBlades.length; i += 1) {
                const b = moonBlades[i];
                if (!b.alive) {
                    continue;
                }
                if (!b.waveActive) {
                    b.waveDelay -= dt;
                    if (b.waveDelay > 0) {
                        continue;
                    }
                    b.waveActive = true;
                }
                b.age += dt;
                if (b.age >= b.life) {
                    b.alive = false;
                    continue;
                }
                b.vx += -b.vy * b.arcDrift * dt;
                b.vy += b.vx * b.arcDrift * dt;
                b.x += b.vx * dtS;
                b.y += b.vy * dtS;
                b.angle = Math.atan2(b.vy, b.vx) + b.spin * dtS;
                if (!b.trailPoints.length || Math.hypot(b.x - b.trailX, b.y - b.trailY) > 4) {
                    b.trailPoints.push({ x: b.x, y: b.y });
                    if (b.trailPoints.length > 7) {
                        b.trailPoints.shift();
                    }
                    b.trailX = b.x;
                    b.trailY = b.y;
                }
                const tp = b.age / b.life;
                const fadeIn = Math.min(1, b.age / 80);
                const fadeOut = tp > 0.65 ? 1 - (tp - 0.65) / 0.35 : 1;
                const alpha = fadeIn * fadeOut * (b.tier === 0 ? 0.92 : b.tier === 1 ? 0.82 : 0.68);
                if (alpha >= 0.02) {
                    drawMoonBlade(b, alpha);
                }
            }
        }

        function drawTrail(now) {
            if (trail.length < 3) {
                return;
            }
            for (let i = 1; i < trail.length; i += 1) {
                const age = (now - trail[i].t) / 380;
                const alpha = clamp(1 - age, 0, 1);
                if (alpha < 0.01) {
                    continue;
                }
                const w = lerp(1.5, 9, 1 - age);
                ctx.beginPath();
                ctx.moveTo(trail[i - 1].x, trail[i - 1].y);
                ctx.lineTo(trail[i].x, trail[i].y);
                ctx.lineWidth = w * 2.8;
                ctx.strokeStyle = "rgba(130,30,200," + alpha * 0.28 + ")";
                ctx.stroke();
                ctx.lineWidth = w * 1.1;
                ctx.strokeStyle = "rgba(200,140,255," + alpha * 0.6 + ")";
                ctx.stroke();
            }
        }

        function updateSparks(dt, dtS) {
            for (let i = 0; i < sparks.length; i += 1) {
                const s = sparks[i];
                if (!s.alive) {
                    continue;
                }
                s.age += dt;
                if (s.age >= s.life) {
                    s.alive = false;
                    continue;
                }
                s.px = s.x;
                s.py = s.y;
                s.x += s.vx * dtS;
                s.y += s.vy * dtS;
                s.vy += 140 * dtS;
                const tp = s.age / s.life;
                const a = clamp((1 - tp) * (1 - tp) * s.bright * 1.2, 0, 1);
                ctx.beginPath();
                ctx.moveTo(s.px, s.py);
                ctx.lineTo(s.x, s.y);
                ctx.lineWidth = clamp(2 - tp * 1.5, 0.4, 2);
                ctx.strokeStyle = s.blood ? bloodColor(1 - tp * 0.55, a) : moonColor(1 - tp * 0.55, a);
                ctx.stroke();
            }
        }

        function updateEmbers(dt, dtS, now) {
            for (let i = 0; i < embers.length; i += 1) {
                const e = embers[i];
                if (!e.alive) {
                    continue;
                }
                e.age += dt;
                if (e.age >= e.life) {
                    e.alive = false;
                    continue;
                }
                e.x += e.vx * dtS + Math.sin(now * 0.0035 + e.phase) * e.sway * dtS;
                e.y += e.vy * dtS;
                e.vy += e.grav * dtS;
                const tp = e.age / e.life;
                const hotness = e.hot * (1 - tp * 0.65);
                const a = (1 - tp) * (1 - tp) * 0.92;
                const r = e.sz * (1 - tp * 0.28);
                if (r < 0.4) {
                    continue;
                }
                ctx.fillStyle = e.blood ? bloodColor(hotness, a) : moonColor(hotness, a);
                ctx.beginPath();
                ctx.arc(e.x, e.y, Math.max(0.4, r), 0, TAU);
                ctx.fill();
            }
        }

        function drawCursorTip(now) {
            const breathe = 0.86 + 0.09 * Math.sin(now * 0.0098) + 0.055 * Math.sin(now * 0.024 + 1.1) + 0.035 * Math.sin(now * 0.041 + 2.4);
            const cx = P.x + Math.sin(now * 0.018);
            const cy = P.y + Math.sin(now * 0.015 + 1.8);

            const vg = ctx.createRadialGradient(cx, cy, 0, cx, cy, 72 * breathe);
            vg.addColorStop(0, "rgba(100,20,180,0.18)");
            vg.addColorStop(0.5, "rgba(50,5,100,0.07)");
            vg.addColorStop(1, "rgba(0,0,0,0)");
            ctx.fillStyle = vg;
            ctx.beginPath();
            ctx.arc(cx, cy, 72 * breathe, 0, TAU);
            ctx.fill();

            const hg = ctx.createRadialGradient(cx, cy, 0, cx, cy, 9 * breathe);
            hg.addColorStop(0, "rgba(255,240,255,1)");
            hg.addColorStop(0.4, "rgba(220,180,255,0.92)");
            hg.addColorStop(0.75, "rgba(160,80,240,0.5)");
            hg.addColorStop(1, "rgba(80,0,160,0)");
            ctx.fillStyle = hg;
            ctx.beginPath();
            ctx.arc(cx, cy, 9 * breathe, 0, TAU);
            ctx.fill();

            ctx.save();
            ctx.globalAlpha = 0.55 * breathe;
            drawCrescent(cx + Math.cos(now * 0.0025) * 14 * breathe, cy + Math.sin(now * 0.0025) * 14 * breathe, 5 * breathe, now * 0.0025 + Math.PI * 0.6, 0.85, false, 0.7);
            ctx.restore();
        }

        function drawHd(dt) {
            hctx.clearRect(0, 0, W, H);
            for (let i = 0; i < hdCells.length; i += 1) {
                const h = hdCells[i];
                if (!h.alive) {
                    continue;
                }
                h.age += dt;
                if (h.age >= h.life) {
                    h.alive = false;
                    continue;
                }
                const tp = h.age / h.life;
                const r = h.str * 18 * (1 - tp * 0.35);
                const a = (1 - tp) * 0.1;
                const g = hctx.createRadialGradient(h.x, h.y, 0, h.x, h.y, r);
                g.addColorStop(0, "rgba(140,60,220," + a + ")");
                g.addColorStop(0.5, "rgba(80,10,120," + a * 0.4 + ")");
                g.addColorStop(1, "rgba(0,0,0,0)");
                hctx.fillStyle = g;
                hctx.beginPath();
                hctx.arc(h.x, h.y, r, 0, TAU);
                hctx.fill();
            }
        }

        window.addEventListener("resize", resize);
        window.addEventListener("mousemove", function (event) {
            setTarget(event.clientX, event.clientY);
        });
        window.addEventListener("touchmove", function (event) {
            if (event.touches.length) {
                setTarget(event.touches[0].clientX, event.touches[0].clientY);
            }
        }, { passive: true });
        window.addEventListener("mousedown", function (event) {
            body.classList.add("aura-active");
            burst(event.clientX, event.clientY);
        });
        window.addEventListener("mouseup", function () {
            body.classList.remove("aura-active");
        });
        window.addEventListener("mouseleave", function () {
            body.classList.remove("aura-active");
        });
        window.addEventListener("touchstart", function (event) {
            body.classList.add("aura-active");
            if (event.touches.length) {
                setTarget(event.touches[0].clientX, event.touches[0].clientY);
                burst(P.tx, P.ty);
            }
        }, { passive: true });
        window.addEventListener("touchend", function () {
            body.classList.remove("aura-active");
        });
        document.addEventListener("visibilitychange", function () {
            if (document.hidden) {
                stopFrame();
            } else {
                lastFrame = performance.now();
                scheduleFrame();
            }
        });

        resize();
        scheduleFrame();
    }
})();
