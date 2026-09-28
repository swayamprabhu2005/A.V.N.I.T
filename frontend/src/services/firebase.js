import { initializeApp, getApps } from "firebase/app";
import { 
  getAuth, 
  signInWithPopup, 
  GoogleAuthProvider, 
  OAuthProvider, 
  signOut,
  onAuthStateChanged 
} from "firebase/auth";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || ""
};

// Check if credentials are placeholders or valid
export const isFirebaseConfigured = () => {
  return (
    Boolean(firebaseConfig.apiKey) && 
    !firebaseConfig.apiKey.includes("ReplaceWith") &&
    Boolean(firebaseConfig.projectId) &&
    !firebaseConfig.projectId.includes("project_id")
  );
};

let app = null;
let auth = null;

try {
  if (!getApps().length) {
    app = initializeApp(firebaseConfig);
  } else {
    app = getApps()[0];
  }
  auth = getAuth(app);
} catch (e) {
  console.warn("[AVNIT Firebase] Notice: Firebase initialization waiting for active project keys.", e);
}

// 1. Google SSO Sign In
export async function signInWithGoogle() {
  if (!auth || !isFirebaseConfigured()) {
    throw new Error("FIREBASE_NOT_CONFIGURED: Please configure your live Firebase credentials in frontend/.env to enable live Google SSO, or use Operator Badge Serial login.");
  }
  const provider = new GoogleAuthProvider();
  provider.setCustomParameters({ prompt: 'select_account' });
  const result = await signInWithPopup(auth, provider);
  return {
    uid: result.user.uid,
    displayName: result.user.displayName || "Google Operator",
    email: result.user.email,
    photoURL: result.user.photoURL,
    provider: "google",
    role: "Traffic Enforcement Officer",
    serialNumber: `SSO-G-${result.user.uid.slice(0, 8).toUpperCase()}`
  };
}

// 2. Microsoft SSO Sign In
export async function signInWithMicrosoft() {
  if (!auth || !isFirebaseConfigured()) {
    throw new Error("FIREBASE_NOT_CONFIGURED: Please configure your live Firebase credentials in frontend/.env to enable live Microsoft SSO, or use Operator Badge Serial login.");
  }
  const provider = new OAuthProvider('microsoft.com');
  provider.setCustomParameters({ prompt: 'consent' });
  const result = await signInWithPopup(auth, provider);
  return {
    uid: result.user.uid,
    displayName: result.user.displayName || "Microsoft Enterprise User",
    email: result.user.email,
    photoURL: result.user.photoURL,
    provider: "microsoft",
    role: "Highway Surveillance Inspector",
    serialNumber: `SSO-MS-${result.user.uid.slice(0, 8).toUpperCase()}`
  };
}

// 3. Official Law Enforcement Operator Badge Serial Key Login (Immediate Access)
export function logInWithSerial(serialKey = "AVNIT-OFFICER-2026", department = "National Highway Patrol") {
  const cleanSerial = serialKey.trim() || "AVNIT-OP-7749";
  const user = {
    uid: `serial_${cleanSerial.toLowerCase()}`,
    displayName: `Officer [Badge ${cleanSerial}]`,
    email: `${cleanSerial.toLowerCase()}@law-enforcement.gov.in`,
    photoURL: null,
    provider: "serial",
    role: "Senior Traffic Enforcement Officer",
    department: department || "National Highway Patrol",
    serialNumber: cleanSerial
  };
  localStorage.setItem("avnit_operator_session", JSON.stringify(user));
  return user;
}

// 4. Get Current Active Operator Session
export function getSavedOperator() {
  const saved = localStorage.getItem("avnit_operator_session");
  if (saved) {
    try {
      return JSON.parse(saved);
    } catch {
      return null;
    }
  }
  return null;
}

// 5. Sign Out
export async function signOutOperator() {
  localStorage.removeItem("avnit_operator_session");
  if (auth) {
    try {
      await signOut(auth);
    } catch {
      // ignore
    }
  }
}
