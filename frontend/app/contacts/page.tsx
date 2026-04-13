import { fetchAPI } from "../../lib/api";

type DoctorProfile = {
  full_name: string;
  address?: string;
  email?: string;
  instagram_url?: string;
  vk_url?: string;
  dzen_url?: string;
  yandex_maps_embed_url?: string;
};

function InstagramIcon() {
  return (
    <svg
      viewBox="0 0 50 50"
      className="h-5 w-5 fill-current"
      aria-hidden="true"
    >
      <path d="M 16 3 C 8.83 3 3 8.83 3 16 L 3 34 C 3 41.17 8.83 47 16 47 L 34 47 C 41.17 47 47 41.17 47 34 L 47 16 C 47 8.83 41.17 3 34 3 L 16 3 z M 37 11 C 38.1 11 39 11.9 39 13 C 39 14.1 38.1 15 37 15 C 35.9 15 35 14.1 35 13 C 35 11.9 35.9 11 37 11 z M 25 14 C 31.07 14 36 18.93 36 25 C 36 31.07 31.07 36 25 36 C 18.93 36 14 31.07 14 25 C 14 18.93 18.93 14 25 14 z M 25 16 C 20.04 16 16 20.04 16 25 C 16 29.96 20.04 34 25 34 C 29.96 34 34 29.96 34 25 C 34 20.04 29.96 16 25 16 z" />
    </svg>
  );
}

function VkIcon() {
  return (
    <svg
      viewBox="0 0 101 100"
      className="h-5 w-5 fill-current"
      aria-hidden="true"
    >
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M7.52944 7.02944C0.5 14.0589 0.5 25.3726 0.5 48V52C0.5 74.6274 0.5 85.9411 7.52944 92.9706C14.5589 100 25.8726 100 48.5 100H52.5C75.1274 100 86.4411 100 93.4706 92.9706C100.5 85.9411 100.5 74.6274 100.5 52V48C100.5 25.3726 100.5 14.0589 93.4706 7.02944C86.4411 0 75.1274 0 52.5 0H48.5C25.8726 0 14.5589 0 7.52944 7.02944ZM17.3752 30.4169C17.9168 56.4169 30.9167 72.0418 53.7084 72.0418H55.0003V57.1668C63.3753 58.0001 69.7082 64.1252 72.2498 72.0418H84.0835C80.8335 60.2085 72.2914 53.6668 66.9581 51.1668C72.2914 48.0835 79.7915 40.5835 81.5831 30.4169H70.8328C68.4995 38.6669 61.5836 46.1668 55.0003 46.8751V30.4169H44.2499V59.2501C37.5833 57.5835 29.1668 49.5002 28.7918 30.4169H17.3752Z"
      />
    </svg>
  );
}

function DzenIcon() {
  return (
    <svg
      viewBox="0 0 169 169"
      className="h-5 w-5 fill-current"
      aria-hidden="true"
    >
      <g clipPath="url(#clip0_45_484)">
        <path d="M84.0337 168.01H84.7036C118.068 168.01 137.434 164.651 151.152 151.333C165.139 137.206 168.369 117.709 168.369 84.4749V83.5351C168.369 50.311 165.139 30.9445 151.152 16.677C137.444 3.3594 117.938 0 84.7136 0H84.0437C50.6797 0 31.3031 3.3594 17.5856 16.677C3.59808 30.8045 0.368652 50.311 0.368652 83.5351V84.4749C0.368652 117.699 3.59808 137.066 17.5856 151.333C31.1732 164.651 50.6797 168.01 84.0337 168.01Z" />
        <path d="M148.369 82.7304C148.369 82.0906 147.849 81.5608 147.209 81.5308C124.246 80.661 110.271 77.732 100.494 67.955C90.6967 58.1581 87.7776 44.1724 86.9079 21.1596C86.8879 20.5198 86.358 20 85.7082 20H83.0291C82.3893 20 81.8594 20.5198 81.8295 21.1596C80.9597 44.1624 78.0406 58.1581 68.2437 67.955C58.4568 77.742 44.4911 80.661 21.5283 81.5308C20.8885 81.5508 20.3687 82.0806 20.3687 82.7304V85.4096C20.3687 86.0494 20.8885 86.5792 21.5283 86.6092C44.4911 87.4789 58.4667 90.408 68.2437 100.185C78.0206 109.962 80.9397 123.908 81.8195 146.83C81.8394 147.47 82.3693 147.99 83.0191 147.99H85.7082C86.348 147.99 86.8779 147.47 86.9079 146.83C87.7876 123.908 90.7067 109.962 100.484 100.185C110.271 90.398 124.236 87.4789 147.199 86.6092C147.839 86.5892 148.359 86.0594 148.359 85.4096V82.7304H148.369Z" fill="white" />
      </g>
      <defs>
        <clipPath id="clip0_45_484">
          <rect width="168.04" height="168.04" transform="translate(0.368652)" />
        </clipPath>
      </defs>
    </svg>
  );
}

function MailIcon() {
  return (
    <svg
      viewBox="0 0 24 24"
      className="h-5 w-5 fill-current"
      aria-hidden="true"
    >
      <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2Zm0 4l-8 5-8-5V6l8 5 8-5v2z" />
    </svg>
  );
}

function SocialIconLink({
  href,
  label,
  children,
  hoverClass,
}: {
  href: string;
  label: string;
  children: React.ReactNode;
  hoverClass?: string;
}) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noreferrer"
      aria-label={label}
      title={label}
      className={`flex h-12 w-12 items-center justify-center rounded-2xl border border-gray-200 text-gray-600 transition hover:scale-105 hover:shadow-sm ${hoverClass || ""}`}
    >
      {children}
    </a>
  );
}

export default async function ContactsPage() {
  const doctor: DoctorProfile | null = await fetchAPI("/profile");

  return (
    <main className="min-h-screen bg-white px-6 py-12">
      <div className="mx-auto max-w-5xl space-y-8">
        <div className="rounded-3xl border border-gray-100 bg-white p-8 shadow-sm">
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-sky-600">
            Контакты
          </p>
          <h1 className="mt-3 text-4xl font-semibold text-gray-900">
            Контактная информация
          </h1>

          <div className="mt-8 grid gap-6 md:grid-cols-2">
            <div className="rounded-3xl bg-sky-50 p-6">
              <h2 className="text-xl font-semibold text-gray-900">
                Основные контакты
              </h2>

              <div className="mt-5 space-y-4 text-gray-700">
                <p>
                  <span className="font-medium text-gray-900">Врач:</span>{" "}
                  {doctor?.full_name || "Не указано"}
                </p>

                <p>
                  <span className="font-medium text-gray-900">Email:</span>{" "}
                  {doctor?.email ? (
                    <a
                      href={`mailto:${doctor.email}`}
                      className="text-sky-600 hover:text-sky-700"
                    >
                      {doctor.email}
                    </a>
                  ) : (
                    "Не указан"
                  )}
                </p>

                <p>
                  <span className="font-medium text-gray-900">Адрес приема:</span>{" "}
                  {doctor?.address || "Не указан"}
                </p>
              </div>
            </div>

            <div className="rounded-3xl bg-white p-6 ring-1 ring-gray-100">
              <h2 className="text-xl font-semibold text-gray-900">
                Социальные сети
              </h2>

              <div className="mt-5 flex flex-wrap gap-3">
                {doctor?.instagram_url ? (
                  <SocialIconLink
                    href={doctor.instagram_url}
                    label="Instagram"
                    hoverClass="hover:border-pink-300 hover:bg-gradient-to-tr hover:from-pink-500 hover:to-purple-500 hover:text-white"
                  >
                    <InstagramIcon />
                  </SocialIconLink>
                ) : null}

                {doctor?.vk_url ? (
                  <SocialIconLink
                    href={doctor.vk_url}
                    label="VK"
                    hoverClass="hover:border-blue-300 hover:bg-blue-600 hover:text-white"
                  >
                    <VkIcon />
                  </SocialIconLink>
                ) : null}

                {doctor?.dzen_url ? (
                  <SocialIconLink
                    href={doctor.dzen_url}
                    label="Дзен"
                    hoverClass="hover:border-gray-900 hover:bg-black hover:text-white"
                  >
                    <DzenIcon />
                  </SocialIconLink>
                ) : null}

                {doctor?.email ? (
                  <SocialIconLink
                    href={`mailto:${doctor.email}`}
                    label="Email"
                    hoverClass="hover:border-gray-700 hover:bg-gray-800 hover:text-white"
                  >
                    <MailIcon />
                  </SocialIconLink>
                ) : null}
              </div>
            </div>
          </div>
        </div>

        {doctor?.yandex_maps_embed_url ? (
          <div className="overflow-hidden rounded-3xl border border-gray-100 bg-white shadow-sm">
            <div className="border-b border-gray-100 px-6 py-5">
              <h2 className="text-xl font-semibold text-gray-900">
                Где проходит очный прием
              </h2>
              <p className="mt-2 text-gray-600">
                Ниже показана встроенная карта с точкой приема.
              </p>
            </div>

            <div className="h-[420px] w-full">
              <iframe
                src={doctor.yandex_maps_embed_url}
                width="100%"
                height="100%"
                allowFullScreen
                loading="lazy"
                className="h-full w-full border-0"
                title="Карта места приема"
              />
            </div>
          </div>
        ) : null}
      </div>
    </main>
  );
}