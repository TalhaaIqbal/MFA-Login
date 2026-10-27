import { Helmet } from 'react-helmet-async'
import { Link } from 'react-router-dom'

function PrivacyPolicy() {
  const lastUpdated = 'January 2026'

  return (
    <>
      <Helmet>
        <title>Privacy Policy | MFA Login</title>
        <meta name="description" content="Privacy Policy for MFA Login - Learn how we collect, use, and protect your personal information." />
      </Helmet>

      <div className="min-h-screen bg-gradient-to-br from-gray-800 to-gray-600 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-xl shadow-2xl p-8 md:p-12">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Privacy Policy</h1>
            <p className="text-gray-600 mb-8">Last updated: {lastUpdated}</p>

            <div className="prose prose-lg max-w-none text-gray-700">
              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Introduction</h2>
                <p className="mb-4">
                  Welcome to MFA Login ("we," "our," or "us"). We are committed to protecting your personal information and your right to privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our authentication service.
                </p>
                <p>
                  Please read this Privacy Policy carefully. If you do not agree with the terms of this Privacy Policy, please do not access or use our service.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Information We Collect</h2>
                
                <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-6">2.1 Personal Information</h3>
                <p className="mb-4">
                  We collect information that you voluntarily provide to us when you register for an account, including:
                </p>
                <ul className="list-disc pl-6 mb-4 space-y-2">
                  <li>Email address</li>
                  <li>Name (full name or display name)</li>
                  <li>Password (encrypted and stored securely)</li>
                  <li>Two-factor authentication (2FA) secrets (encrypted)</li>
                </ul>

                <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-6">2.2 Authentication Data</h3>
                <p className="mb-4">
                  We collect and store the following authentication-related information:
                </p>
                <ul className="list-disc pl-6 mb-4 space-y-2">
                  <li>Session identifiers (for maintaining your login session)</li>
                  <li>Login timestamps and IP addresses (for security monitoring)</li>
                  <li>Device information (for security purposes)</li>
                </ul>

                <h3 className="text-xl font-semibold text-gray-800 mb-3 mt-6">2.3 Automatically Collected Information</h3>
                <p className="mb-4">
                  When you access our service, we automatically collect certain information about your device, including:
                </p>
                <ul className="list-disc pl-6 mb-4 space-y-2">
                  <li>IP address</li>
                  <li>Browser type and version</li>
                  <li>Operating system</li>
                  <li>Referring website</li>
                  <li>Pages visited and time spent on those pages</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. How We Use Your Information</h2>
                <p className="mb-4">We use the information we collect in the following ways:</p>
                <ul className="list-disc pl-6 mb-4 space-y-2">
                  <li><strong>Authentication:</strong> To provide and maintain your account access</li>
                  <li><strong>Security:</strong> To protect your account and prevent unauthorized access</li>
                  <li><strong>Two-Factor Authentication:</strong> To enable and manage 2FA for enhanced security</li>
                  <li><strong>Service Improvement:</strong> To analyze usage patterns and improve our service</li>
                  <li><strong>Communications:</strong> To send you important security alerts and service updates</li>
                  <li><strong>Compliance:</strong> To comply with legal obligations and enforce our terms</li>
                </ul>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Data Security</h2>
                <p className="mb-4">
                  We implement appropriate technical and organizational measures to protect your personal information, including:
                </p>
                <ul className="list-disc pl-6 mb-4 space-y-2">
                  <li><strong>Encryption:</strong> Passwords and 2FA secrets are encrypted using industry-standard encryption (Fernet)</li>
                  <li><strong>Secure Storage:</strong> Data is stored in MongoDB with appropriate access controls</li>
                  <li><strong>Secure Transmission:</strong> All data is transmitted over HTTPS (in production)</li>
                  <li><strong>Session Management:</strong> Sessions are securely managed with expiration and revocation capabilities</li>
                  <li><strong>Access Controls:</strong> Only authorized personnel have access to your data</li>
                </ul>
                <p className="mt-4">
                  However, no method of transmission over the Internet or electronic storage is 100% secure. While we strive to use commercially acceptable means to protect your personal information, we cannot guarantee its absolute security.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Data Retention</h2>
                <p className="mb-4">
                  We retain your personal information for as long as necessary to provide our services and fulfill the purposes outlined in this Privacy Policy, including:
                </p>
                <ul className="list-disc pl-6 mb-4 space-y-2">
                  <li>Account information: Retained while your account is active</li>
                  <li>Session data: Retained for 30 days or until session expires</li>
                  <li>Login logs: Retained for security monitoring and audit purposes (up to 1 year)</li>
                </ul>
                <p>
                  When you delete your account, we will delete or anonymize your personal information within a reasonable time frame, except where we are required by law to retain it.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Your Privacy Rights</h2>
                <p className="mb-4">Depending on your location, you may have the following rights regarding your personal information:</p>
                <ul className="list-disc pl-6 mb-4 space-y-2">
                  <li><strong>Access:</strong> Request access to your personal information</li>
                  <li><strong>Correction:</strong> Request correction of inaccurate information</li>
                  <li><strong>Deletion:</strong> Request deletion of your personal information</li>
                  <li><strong>Portability:</strong> Request transfer of your data to another service</li>
                  <li><strong>Objection:</strong> Object to processing of your personal information</li>
                  <li><strong>Restriction:</strong> Request restriction of processing of your personal information</li>
                </ul>
                <p className="mt-4">
                  To exercise these rights, please contact us using the information provided below.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Cookies and Tracking</h2>
                <p className="mb-4">
                  We use cookies and similar tracking technologies to track activity on our service and hold certain information. Cookies are files with a small amount of data which may include an anonymous unique identifier.
                </p>
                <p className="mb-4">
                  We use cookies for:
                </p>
                <ul className="list-disc pl-6 mb-4 space-y-2">
                  <li><strong>Session Management:</strong> To maintain your login session (HttpOnly cookies)</li>
                  <li><strong>Security:</strong> To detect and prevent fraudulent activity</li>
                  <li><strong>Preferences:</strong> To remember your settings and preferences</li>
                </ul>
                <p>
                  You can instruct your browser to refuse all cookies or to indicate when a cookie is being sent. However, if you do not accept cookies, you may not be able to use some portions of our service.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Third-Party Services</h2>
                <p className="mb-4">
                  Our service may contain links to third-party websites or services. We have no control over and assume no responsibility for the content, privacy policies, or practices of any third-party sites or services.
                </p>
                <p>
                  We encourage you to review the privacy policies of any third-party sites you visit.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. Children's Privacy</h2>
                <p>
                  Our service is not intended for children under the age of 13. We do not knowingly collect personal information from children under 13. If you are a parent or guardian and you believe your child has provided us with personal information, please contact us, and we will delete such information.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. Changes to This Privacy Policy</h2>
                <p>
                  We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the "Last updated" date. You are advised to review this Privacy Policy periodically for any changes.
                </p>
              </section>

              <section className="mb-8">
                <h2 className="text-2xl font-semibold text-gray-900 mb-4">11. Contact Us</h2>
                <p className="mb-4">
                  If you have any questions about this Privacy Policy, please contact us:
                </p>
                <ul className="list-none space-y-2">
                  <li><strong>Email:</strong> admin@example.com</li>
                  <li><strong>Website:</strong> <Link to="/" className="text-emerald-600 hover:text-emerald-700">MFA Login</Link></li>
                </ul>
              </section>
            </div>

            <div className="mt-12 pt-8 border-t border-gray-200">
              <p className="text-sm text-gray-500 text-center">
                By using our service, you acknowledge that you have read and understood this Privacy Policy.
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default PrivacyPolicy
